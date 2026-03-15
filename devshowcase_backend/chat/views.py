import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
GROQ_MODEL = 'llama-3.3-70b-versatile'

BASE_SYSTEM_PROMPT = (
    "You are a helpful assistant for the DevShowcase platform, specialising in API development, "
    "sandbox testing, and error debugging. Keep your replies concise — 300 words or fewer — "
    "unless the user explicitly asks for more detail. When the context includes an error, "
    "explain the error first before addressing anything else. "
    "When asked for test case suggestions, organise them into three labelled categories: "
    "Happy Path, Edge Cases, and Error Scenarios. For each test case include the input "
    "conditions, the expected response status code, and the expected response behaviour."
)


def _build_messages(message, history, error_context, endpoint_context):
    """Build the Groq messages array from request data."""
    system_content = BASE_SYSTEM_PROMPT

    # Inject error-context focus instructions into the system prompt
    if error_context:
        status_code = error_context.get('status_code')
        if status_code is not None:
            if 400 <= status_code <= 499:
                system_content += (
                    " The user has encountered a client-side error. Focus your response on "
                    "client-side causes such as invalid request body, missing parameters, or "
                    "authentication issues."
                )
            elif 500 <= status_code <= 599:
                system_content += (
                    " The user has encountered a server-side error. Focus your response on "
                    "server-side causes such as misconfiguration, missing environment variables, "
                    "or unhandled exceptions."
                )

    messages = [{"role": "system", "content": system_content}]

    # Append history (capped at 10 most recent messages)
    capped_history = (history or [])[-10:]
    messages.extend(capped_history)

    # Build the final user message, optionally prepending context
    context_prefix = ""

    if error_context:
        method = error_context.get('method', '')
        path = error_context.get('path', '')
        status_code = error_context.get('status_code', '')
        error_message = error_context.get('error_message', '')
        context_prefix += (
            f"[Error context] {method} {path} returned {status_code}: {error_message}\n\n"
        )

    if endpoint_context:
        method = endpoint_context.get('method', '')
        path = endpoint_context.get('path', '')
        parameters = endpoint_context.get('parameters', [])
        expected_responses = endpoint_context.get('expected_responses', [])
        sample_body = endpoint_context.get('sample_body')
        description = endpoint_context.get('description', '')
        context_prefix += (
            f"[Endpoint context] {method} {path}\n"
        )
        if description:
            context_prefix += f"Description: {description}\n"
        if sample_body:
            context_prefix += f"Sample request body: {sample_body}\n"
        if parameters:
            context_prefix += f"Path parameters: {parameters}\n"
        if expected_responses:
            context_prefix += f"Expected responses: {expected_responses}\n"
        context_prefix += "\n"

    final_user_content = context_prefix + message
    messages.append({"role": "user", "content": final_user_content})

    return messages


@api_view(['POST'])
@permission_classes([AllowAny])
def chat_view(request):
    data = request.data

    message = data.get('message', '')
    if not message or not str(message).strip():
        return Response({'error': 'message field is required'}, status=400)

    history = data.get('history', [])
    error_context = data.get('error_context')
    endpoint_context = data.get('endpoint_context')

    messages = _build_messages(str(message), history, error_context, endpoint_context)

    try:
        groq_response = requests.post(
            GROQ_API_URL,
            headers={
                'Authorization': f'Bearer {settings.GROQ_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'model': GROQ_MODEL,
                'messages': messages,
            },
            timeout=30,
        )

        if groq_response.status_code != 200:
            return Response({'error': 'AI service unavailable'}, status=503)

        reply = groq_response.json()['choices'][0]['message']['content']
        return Response({'reply': reply}, status=200)

    except requests.exceptions.Timeout:
        return Response({'error': 'AI service unavailable'}, status=503)
    except Exception:
        return Response({'error': 'AI service unavailable'}, status=503)
