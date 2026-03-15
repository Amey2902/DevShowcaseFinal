# Implementation Plan: AI Chatbot Assistant

## Overview

Implement a floating chat widget on the frontend backed by a new stateless Django `chat` app. The backend forwards messages and context to Groq (`llama-3.3-70b-versatile`) and returns AI replies. Context (errors, selected endpoints) is injected from `APIPlayground.jsx`.

## Tasks

- [x] 1. Create the Django `chat` app
  - [x] 1.1 Scaffold `devshowcase_backend/chat/` with `apps.py`, `urls.py`, and `views.py`
    - Create `apps.py` with `ChatConfig` (name = `'chat'`)
    - Create `urls.py` with a single route: `path('chat/', chat_view)`
    - Create `views.py` with `chat_view` as `@api_view(['POST'])` / `@permission_classes([AllowAny])`
    - View must validate `message` (missing or blank → 400), build the Groq messages array (system prompt + history capped at 10 + contextual injection + user message), call Groq via `requests.post` with a 30-second timeout, return `{"reply": "..."}` on success or 503 on Groq failure/timeout
    - System prompt must instruct the AI to act as a DevShowcase assistant, keep replies ≤ 300 words, use `llama-3.3-70b-versatile`
    - When `error_context.status_code` is 400–499, inject client-side focus instructions; 500–599 → server-side focus
    - When `endpoint_context` is present, inject endpoint details so the AI can suggest structured test cases (Happy Path / Edge Cases / Error Scenarios)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 5.1, 5.2, 5.3, 5.4, 3.3, 3.4, 3.5, 3.6, 6.1, 6.2, 6.4, 6.5, 6.6_

  - [ ]* 1.2 Write property test — Property 1: missing/blank message returns 400
    - **Property 1: Missing message returns 400**
    - **Validates: Requirements 4.3**
    - Use `hypothesis` with `@given(message=st.one_of(st.just(""), st.text(alphabet=st.characters(whitelist_categories=("Zs",)))))` and `@settings(max_examples=100)`

  - [ ]* 1.3 Write property test — Property 2: valid message returns 200 with reply
    - **Property 2: Valid request returns reply**
    - **Validates: Requirements 4.2**
    - Mock `requests.post` to return a fixed Groq response; assert `status == 200` and `response.json()['reply']` is non-empty

  - [ ]* 1.4 Write property test — Property 3: history forwarded in order
    - **Property 3: History is forwarded to Groq**
    - **Validates: Requirements 4.5**
    - Capture the messages array passed to the mocked Groq call; assert history messages appear in the same order after the system message

  - [ ]* 1.5 Write property test — Property 4: error context shapes system prompt
    - **Property 4: Error context shapes the system prompt**
    - **Validates: Requirements 3.3, 3.5, 3.6**
    - `@given(status_code=st.integers(min_value=400, max_value=499))` → assert `'client'` in system message content; repeat for 500–599 → `'server'`

  - [ ]* 1.6 Write property test — Property 6: history capped at 10
    - **Property 6: History cap — at most 10 messages forwarded**
    - **Validates: Requirements 4.5**
    - `@given(history=st.lists(..., min_size=11, max_size=30))` → assert history messages forwarded to Groq ≤ 10

  - [ ]* 1.7 Write property test — Property 5: endpoint context forwarded to Groq
    - **Property 5: Endpoint context is forwarded to Groq**
    - **Validates: Requirements 6.4**
    - Assert that when `endpoint_context` is present, the captured Groq messages array contains the endpoint method and path

- [x] 2. Register the `chat` app and wire its URL
  - [x] 2.1 Add `'chat'` to `INSTALLED_APPS` in `devshowcase_backend/config/settings.py`
    - _Requirements: 4.1_

  - [x] 2.2 Add `path('api/', include('chat.urls'))` to `devshowcase_backend/config/urls.py`
    - _Requirements: 4.1_

- [ ] 3. Checkpoint — backend wired and tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Build `ChatWidget.jsx` and `ChatWidget.css`
  - [x] 4.1 Create `devshowcase_frontend/src/components/ChatWidget.jsx`
    - Floating button fixed to bottom-right; clicking toggles `isOpen`
    - When open, render message history area and text input with send button
    - On submit (Enter or button click): append user message to `messages`, POST to `/api/chat/` with `{ message, history: messages.slice(-10), error_context, endpoint_context }`, append AI reply; show loading indicator while awaiting
    - On fetch error or non-2xx response, append fallback message: "The assistant is temporarily unavailable. Please try again."
    - When `errorContext` prop is set, show a dismissible banner above the input offering to explain the error; clicking it pre-populates the input with the error details
    - Accept `errorContext` and `endpointContext` as props
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 3.1, 3.2, 6.3_

  - [x] 4.2 Create `devshowcase_frontend/src/components/ChatWidget.css`
    - Use existing CSS custom properties (`--bg-secondary`, `--accent-primary`, `--text-primary`, etc.)
    - Fixed positioning bottom-right, z-index above page content
    - Chat panel with scrollable message history, distinct user/assistant bubble styles
    - _Requirements: 1.1_

  - [ ]* 4.3 Write frontend unit tests — Property 7: widget toggles open/closed
    - **Property 7: Chat widget toggles open and closed**
    - **Validates: Requirements 1.2, 1.3**
    - Use Vitest + React Testing Library; render `<ChatWidget />`; click floating button → assert panel visible; click again → assert panel hidden

  - [ ]* 4.4 Write frontend unit tests — Property 8: submitted message appears in history
    - **Property 8: Submitted message appears in history**
    - **Validates: Requirements 2.1**
    - Mock `fetch`; type a message and submit; assert the message text appears in the rendered message list

  - [ ]* 4.5 Write frontend unit tests — additional widget behaviours
    - Loading indicator shown while awaiting response
    - Fallback message shown on fetch error
    - Enter key submits the form
    - Empty input does not trigger a POST
    - _Requirements: 2.2, 2.4, 2.5_

- [x] 5. Mount `<ChatWidget />` in `App.jsx`
  - [x] 5.1 Import `ChatWidget` and render it inside `<Router>` but outside `<Routes>` in `devshowcase_frontend/src/App.jsx`
    - Lift `errorContext` and `endpointContext` state up to `App.jsx`; pass setters down and values as props to `<ChatWidget />`
    - _Requirements: 1.4_

- [x] 6. Inject error and endpoint context from `APIPlayground.jsx`
  - [x] 6.1 Add `onErrorContext` and `onEndpointContext` callback props to `APIPlayground`
    - After a failed sandbox or live test (non-2xx or network error), call `onErrorContext({ method, path, status_code, error_message })`
    - When an endpoint is selected (`handleEndpointSelect`), call `onEndpointContext({ method, path, parameters, expected_responses })`
    - Pass these callbacks through `ProjectView` (or wherever `APIPlayground` is rendered) down from `App.jsx`
    - _Requirements: 3.1, 3.2, 6.3_

- [ ] 7. Final checkpoint — full integration working
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Property tests use `hypothesis`; frontend tests use Vitest + React Testing Library
- The backend is stateless — no new database models needed
- History is capped at 10 messages on the frontend before sending; the backend also enforces this cap
