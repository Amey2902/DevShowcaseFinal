# Requirements Document

## Introduction

This feature adds an AI-powered chatbot assistant to the DevShowcase platform. The chatbot is accessible from within the app UI as a floating widget and provides contextual help to users. Its primary use case is assisting users when they encounter errors during sandbox execution or API testing — for example, explaining a test case failure, suggesting fixes, or clarifying what an error response means. The chatbot uses the existing Groq AI integration already present in the backend.

## Glossary

- **Chatbot**: The AI-powered conversational assistant embedded in the DevShowcase UI.
- **Chat_Widget**: The floating UI component rendered on the frontend that users interact with to send and receive messages.
- **Chat_API**: The Django REST API endpoint that receives user messages and returns AI-generated responses.
- **Conversation_Context**: The structured data passed to the AI containing the user's message, the current error (if any), and recent conversation history.
- **Error_Context**: The error payload from a sandbox execution or API test result, including status code, error message, and endpoint details.
- **Groq_Client**: The existing Groq AI HTTP client used in the backend (via `GROQ_API_KEY` in settings).
- **User**: An authenticated or unauthenticated visitor using the DevShowcase platform.
- **Sandbox_Response**: The response object returned by `SandboxService.execute_sandbox_request`, containing `status_code`, `data`, and `error` fields.

---

## Requirements

### Requirement 1: Chat Widget Accessibility

**User Story:** As a user, I want a chatbot widget always accessible in the app UI, so that I can ask for help at any time without leaving my current page.

#### Acceptance Criteria

1. THE Chat_Widget SHALL render as a floating button fixed to the bottom-right corner of every page in the application.
2. WHEN the user clicks the floating button, THE Chat_Widget SHALL expand to display the chat interface including a message history area and a text input field.
3. WHEN the user clicks the floating button while the chat interface is open, THE Chat_Widget SHALL collapse back to the floating button state.
4. THE Chat_Widget SHALL remain visible and accessible across all routes in the React application without requiring a page reload.

---

### Requirement 2: Basic Chat Interaction

**User Story:** As a user, I want to type messages and receive AI responses in the chatbot, so that I can get help with questions about the platform or my API.

#### Acceptance Criteria

1. WHEN the user types a message and submits it, THE Chat_Widget SHALL display the user's message in the message history area immediately.
2. WHEN a user message is submitted, THE Chat_Widget SHALL send the message to the Chat_API and display a loading indicator while awaiting a response.
3. WHEN the Chat_API returns a response, THE Chat_Widget SHALL display the AI response in the message history area below the user's message.
4. IF the Chat_API returns an error, THEN THE Chat_Widget SHALL display a fallback message informing the user that the assistant is temporarily unavailable.
5. THE Chat_Widget SHALL allow the user to submit a message by pressing the Enter key or clicking a send button.
6. THE Chat_Widget SHALL preserve the conversation history for the duration of the browser session so the user can scroll through prior messages.

---

### Requirement 3: Contextual Error Assistance

**User Story:** As a user, I want the chatbot to automatically receive context about errors I encounter during sandbox testing, so that I can get targeted help without manually describing the problem.

#### Acceptance Criteria

1. WHEN a sandbox execution or API test produces an error response, THE Chat_Widget SHALL display a prompt offering to explain the error to the user.
2. WHEN the user accepts the error explanation prompt, THE Chat_Widget SHALL open and pre-populate a message containing the Error_Context including the endpoint method, path, status code, and error message.
3. WHEN the Chat_API receives a message containing an Error_Context, THE Chat_API SHALL include the error details in the Conversation_Context sent to the Groq_Client so the AI can provide a targeted explanation.
4. THE Chat_API SHALL instruct the Groq_Client to respond with a plain-language explanation of the error and at least one actionable suggestion for resolving it.
5. IF the Error_Context contains a status code in the range 400–499, THEN THE Chat_API SHALL instruct the Groq_Client to focus the response on client-side causes such as invalid request body, missing parameters, or authentication issues.
6. IF the Error_Context contains a status code in the range 500–599, THEN THE Chat_API SHALL instruct the Groq_Client to focus the response on server-side causes such as misconfiguration, missing environment variables, or unhandled exceptions.

---

### Requirement 4: Chat API Backend

**User Story:** As a developer, I want a dedicated Chat API endpoint in the Django backend, so that the frontend can send messages and receive AI-generated responses reliably.

#### Acceptance Criteria

1. THE Chat_API SHALL expose a POST endpoint at `/api/chat/` that accepts a JSON body containing a `message` field and an optional `error_context` field.
2. WHEN a valid request is received, THE Chat_API SHALL forward the message and Conversation_Context to the Groq_Client and return the AI response as a JSON object with a `reply` field.
3. IF the `message` field is absent or empty in the request body, THEN THE Chat_API SHALL return a 400 status code with a descriptive error message.
4. IF the Groq_Client request fails or times out, THEN THE Chat_API SHALL return a 503 status code with an error message indicating the AI service is unavailable.
5. THE Chat_API SHALL accept an optional `history` field containing up to 10 prior message objects, each with `role` and `content` fields, and include them in the Conversation_Context to maintain conversational continuity.
6. THE Chat_API SHALL be accessible to unauthenticated users so that all visitors can use the chatbot without logging in.

---

### Requirement 5: AI Response Quality

**User Story:** As a user, I want the chatbot to give helpful, focused responses about DevShowcase and API development, so that the assistant stays relevant and useful.

#### Acceptance Criteria

1. THE Chat_API SHALL include a system prompt in every Groq_Client request that instructs the AI to act as a helpful assistant for the DevShowcase platform, specializing in API development, sandbox testing, and error debugging.
2. THE Chat_API SHALL instruct the Groq_Client to keep responses concise, with a maximum of 300 words per reply, unless the user explicitly requests more detail.
3. WHEN the Conversation_Context includes an Error_Context, THE Chat_API SHALL instruct the Groq_Client to prioritize explaining the error before answering any other part of the user's message.
4. THE Chat_API SHALL use the `llama-3.3-70b-versatile` model via the Groq_Client, consistent with the existing AI features in the platform.

---

### Requirement 6: Test Case Generation Assistance

**User Story:** As a developer, I want the chatbot to suggest test cases for my API endpoints, so that I can improve my test coverage without having to think through every scenario manually.

#### Acceptance Criteria

1. WHEN a user asks the chatbot for test case suggestions for an endpoint (e.g. "what should I test for this POST /users endpoint?"), THE Chat_API SHALL return a structured list of test cases covering happy path, edge case, and error scenarios.
2. THE Chat_API SHALL instruct the Groq_Client to organise test case suggestions into three labelled categories: Happy Path, Edge Cases, and Error Scenarios.
3. WHEN the Chat_Widget is open while the user has an endpoint selected in the API Playground, THE Chat_Widget SHALL inject the selected endpoint's details — including HTTP method, path, parameters, and expected responses — as an `endpoint_context` field in the request body sent to the Chat_API.
4. WHEN the Chat_API receives a request containing an `endpoint_context` field, THE Chat_API SHALL include the endpoint details in the Conversation_Context forwarded to the Groq_Client so the AI can generate targeted test case suggestions specific to that endpoint.
5. IF no `endpoint_context` is provided, THEN THE Chat_API SHALL still attempt to generate test case suggestions based solely on the information present in the user's message.
6. THE Chat_API SHALL instruct the Groq_Client to include, for each suggested test case, the input conditions, the expected response status code, and the expected response behaviour.
