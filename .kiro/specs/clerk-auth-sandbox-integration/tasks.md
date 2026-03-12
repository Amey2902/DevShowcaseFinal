# Implementation Plan: Clerk Authentication and Sandbox Mode Integration

## Overview

This implementation plan breaks down the integration of Clerk JWT authentication and isolated sandbox environments into discrete coding tasks. The implementation follows a layered approach: authentication layer first, then sandbox data models, sandbox service logic, execution routing, and finally frontend integration. Each task builds incrementally to ensure testable progress at every step.

## Tasks

- [x] 1. Complete ClerkAuthentication class with JWKS verification
  - Complete the `authenticate` method in `devshowcase_backend/accounts/authentication.py`
  - Implement `get_jwks` method with caching to fetch public keys from Clerk
  - Add JWT signature verification using RS256 algorithm with PyJWT
  - Extract user ID from 'sub' claim and get-or-create Django User
  - Handle authentication errors (invalid signature, expired token, audience mismatch)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10_

- [ ]* 1.1 Write property tests for ClerkAuthentication
  - **Property 1: Bearer Token Extraction** - Validates: Requirements 1.1
  - **Property 2: JWT Validation** - Validates: Requirements 1.3, 1.4, 1.5
  - **Property 3: User Creation from JWT** - Validates: Requirements 1.6, 1.7
  - **Property 29: Dual Authentication Support** - Validates: Requirements 12.1, 12.2, 12.3

- [ ]* 1.2 Write unit tests for ClerkAuthentication
  - Test JWKS fetching with mocked Clerk endpoint
  - Test specific valid/invalid token scenarios
  - Test user creation vs. retrieval
  - Test error messages for expired/invalid tokens
  - Test authentication fallback order (Clerk → Token)

- [x] 2. Update Django settings for dual authentication
  - Add ClerkAuthentication to REST_FRAMEWORK authentication classes (before TokenAuthentication)
  - Add 'sandbox' to INSTALLED_APPS
  - Verify CLERK_DOMAIN and CLERK_AUDIENCE environment variables are configured
  - _Requirements: 9.1, 9.2, 9.4, 9.5, 11.3, 12.1, 12.4_

- [x] 3. Create sandbox data models
  - [x] 3.1 Implement SandboxEnvironment model
    - Create model with OneToOneField to Project (cascade delete)
    - Add created_at auto timestamp field
    - _Requirements: 10.1, 10.6_
  
  - [x] 3.2 Implement SandboxCollection model
    - Create model with ForeignKey to SandboxEnvironment (cascade delete)
    - Add name CharField
    - Add unique_together constraint on (environment, name)
    - _Requirements: 10.2, 10.4_
  
  - [x] 3.3 Implement SandboxRecord model
    - Create model with ForeignKey to SandboxCollection (cascade delete)
    - Add data JSONField
    - Add created_at and updated_at auto timestamp fields
    - _Requirements: 10.3, 10.5, 10.7_

- [ ]* 3.4 Write property tests for sandbox models
  - **Property 23: Cascade Deletion** - Validates: Requirements 7.3, 10.8, 10.9
  - **Property 25: Collection Name Uniqueness** - Validates: Requirements 10.4
  - **Property 26: Auto-Timestamp Creation** - Validates: Requirements 10.6
  - **Property 27: Auto-Timestamp Update** - Validates: Requirements 10.7

- [ ]* 3.5 Write unit tests for sandbox models
  - Test one-to-one relationship (Project ↔ SandboxEnvironment)
  - Test foreign key relationships
  - Test cascade deletion behavior
  - Test unique constraint on collection names
  - Test JSON field storage and retrieval
  - Test auto-timestamp behavior

- [x] 4. Create database migrations for sandbox models
  - Generate migrations for SandboxEnvironment, SandboxCollection, SandboxRecord
  - Verify migration includes cascade delete constraints
  - Verify migration includes unique_together constraint
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.8, 10.9_

- [x] 5. Implement SandboxService core methods
  - [x] 5.1 Implement extract_resource_name static method
    - Parse URL to extract path component
    - Filter out 'api', version strings (v1, v2), and numeric IDs
    - Return first valid resource segment
    - _Requirements: 3.2_
  
  - [x] 5.2 Implement generate_sandbox static method
    - Get or create SandboxEnvironment for project
    - Extract resource names from all endpoint URLs
    - Create SandboxCollections for each unique resource
    - Process sample_response data (arrays and objects)
    - Create SandboxRecords with duplicate detection
    - _Requirements: 3.1, 3.3, 3.4, 3.5, 3.6, 3.7_

- [ ]* 5.3 Write property tests for sandbox generation
  - **Property 5: Sandbox Environment Creation** - Validates: Requirements 3.1, 3.6
  - **Property 6: Resource Name Extraction** - Validates: Requirements 3.2
  - **Property 7: Collection Creation from Resources** - Validates: Requirements 3.3
  - **Property 8: Array Response Processing** - Validates: Requirements 3.4
  - **Property 9: Object Response Processing** - Validates: Requirements 3.5
  - **Property 10: Duplicate Record Prevention** - Validates: Requirements 3.7

- [ ]* 5.4 Write unit tests for sandbox generation
  - Test generation with empty project (no endpoints)
  - Test generation with single endpoint
  - Test generation with array vs. object sample responses
  - Test generation idempotence (calling twice)
  - Test resource extraction from various URL formats

- [ ] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement SandboxService execution methods
  - [x] 7.1 Implement _extract_id_from_url static method
    - Extract numeric ID from URL path segments
    - Return None if no ID found
    - _Requirements: 4.5, 4.7, 4.8, 4.9_
  
  - [x] 7.2 Implement _handle_get static method
    - Check if URL contains ID
    - Return single record if ID present, all records otherwise
    - Return 404 if specific record not found
    - _Requirements: 4.4, 4.5_
  
  - [x] 7.3 Implement _handle_post static method
    - Generate new ID for record
    - Merge body data with generated ID
    - Create new SandboxRecord
    - Return created record with 201 status
    - _Requirements: 4.6_
  
  - [x] 7.4 Implement _handle_put static method
    - Extract ID from URL
    - Find existing record
    - Replace record data with body (preserve ID)
    - Return 200 with updated data or 404 if not found
    - _Requirements: 4.7_
  
  - [x] 7.5 Implement _handle_patch static method
    - Extract ID from URL
    - Find existing record
    - Merge body data with existing data
    - Return 200 with updated data or 404 if not found
    - _Requirements: 4.8_
  
  - [x] 7.6 Implement _handle_delete static method
    - Extract ID from URL
    - Find and delete record
    - Return 204 No Content or 404 if not found
    - _Requirements: 4.9_
  
  - [x] 7.7 Implement execute_sandbox_request static method
    - Extract resource name from endpoint URL
    - Find corresponding SandboxCollection
    - Route to appropriate HTTP method handler
    - Return structured response with mode, status_code, data, error
    - Handle collection not found errors
    - _Requirements: 4.1, 4.2, 4.10, 4.11, 4.12, 4.13_

- [ ]* 7.8 Write property tests for sandbox execution
  - **Property 11: Sandbox Routing Decision** - Validates: Requirements 4.1, 4.2, 4.3
  - **Property 12: Sandbox GET All Records** - Validates: Requirements 4.4
  - **Property 13: Sandbox GET Single Record** - Validates: Requirements 4.5
  - **Property 14: Sandbox POST Record Creation** - Validates: Requirements 4.6
  - **Property 15: Sandbox PUT Record Replacement** - Validates: Requirements 4.7
  - **Property 16: Sandbox PATCH Record Merging** - Validates: Requirements 4.8
  - **Property 17: Sandbox DELETE Record Removal** - Validates: Requirements 4.9
  - **Property 18: Sandbox Isolation** - Validates: Requirements 4.11, 7.2
  - **Property 24: Sandbox Data Isolation** - Validates: Requirements 7.4, 7.5

- [ ]* 7.9 Write unit tests for sandbox execution
  - Test each HTTP method with specific data
  - Test 404 responses for missing collections/records
  - Test response format structure
  - Test ID extraction from various URL formats
  - Test error handling for edge cases

- [x] 8. Create sandbox views and serializers
  - [x] 8.1 Implement generate_sandbox view
    - Add @api_view(['POST']) decorator
    - Add @permission_classes([IsAuthenticated]) decorator
    - Verify user owns the project (return 404 if not)
    - Call SandboxService.generate_sandbox
    - Return JSON response with environment_id and collections summary
    - _Requirements: 3.8, 3.9, 8.2, 11.1, 11.2_
  
  - [x] 8.2 Create sandbox URL patterns
    - Create `devshowcase_backend/sandbox/urls.py`
    - Add URL pattern for generate_sandbox view
    - _Requirements: 11.1, 11.4_

- [ ]* 8.3 Write unit tests for sandbox views
  - Test successful sandbox generation
  - Test ownership verification (non-owner returns 404)
  - Test authentication requirement
  - Test response format

- [-] 9. Modify execution view for hybrid routing
  - [x] 9.1 Add sandbox existence check
    - Check if project.sandbox exists (one-to-one relationship)
    - Store sandbox environment if exists
    - _Requirements: 4.1_
  
  - [x] 9.2 Add authorization check for write operations
    - Check if user is authenticated
    - If not authenticated and method is POST/PUT/PATCH/DELETE, return 403
    - Allow GET requests for unauthenticated users
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_
  
  - [x] 9.3 Add sandbox routing logic
    - If sandbox exists, call SandboxService.execute_sandbox_request
    - If sandbox doesn't exist, use existing proxy logic
    - Return unified response format with "mode" field
    - _Requirements: 4.2, 4.3_
  
  - [x] 9.4 Update response format
    - Ensure response includes: mode, status_code, data, error
    - Maintain backward compatibility with existing proxy responses
    - _Requirements: 4.10, 11.5_

- [ ]* 9.5 Write property tests for execution view
  - **Property 19: Write Operation Authorization** - Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5
  - **Property 20: Authenticated User Access** - Validates: Requirements 5.6
  - **Property 28: Response Format Consistency** - Validates: Requirements 11.5

- [ ]* 9.6 Write unit tests for execution view
  - Test sandbox routing when sandbox exists
  - Test proxy routing when sandbox doesn't exist
  - Test authorization for each HTTP method
  - Test response format structure
  - Test error handling

- [ ] 10. Implement rate limiting for execution endpoint
  - [ ] 10.1 Create ExecutionRateThrottle class
    - Create `devshowcase_backend/execution/throttles.py`
    - Extend AnonRateThrottle
    - Set rate to '10/min'
    - Implement get_cache_key based on IP address
    - _Requirements: 6.1, 6.3_
  
  - [ ] 10.2 Apply throttle to execute_endpoint view
    - Add @throttle_classes([ExecutionRateThrottle]) decorator
    - Verify 429 response on rate limit exceeded
    - _Requirements: 6.2, 6.5_

- [ ]* 10.3 Write property tests for rate limiting
  - **Property 21: Rate Limit Independence** - Validates: Requirements 6.3
  - **Property 22: Rate Limit Application** - Validates: Requirements 6.5

- [ ]* 10.4 Write unit tests for rate limiting
  - Test exactly 10 requests succeed
  - Test 11th request fails with 429
  - Test different IPs tracked independently
  - Test rate limit reset after 60 seconds

- [x] 11. Register sandbox URLs in main URL configuration
  - Add sandbox URL patterns to `devshowcase_backend/devshowcase_backend/urls.py`
  - Include path('api/sandbox/', include('sandbox.urls'))
  - _Requirements: 11.4_

- [ ] 12. Checkpoint - Backend integration complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Set up Clerk React SDK in frontend
  - [x] 13.1 Install Clerk React package
    - Run: `npm install @clerk/clerk-react` (or yarn equivalent)
    - _Requirements: 2.1_
  
  - [x] 13.2 Configure environment variables
    - Add VITE_CLERK_PUBLISHABLE_KEY to `.env` file
    - Document required environment variable
    - _Requirements: 2.2, 9.3, 9.6_
  
  - [x] 13.3 Wrap App with ClerkProvider
    - Import ClerkProvider from @clerk/clerk-react
    - Wrap root component with ClerkProvider
    - Pass publishableKey from environment variable
    - _Requirements: 2.1, 2.2_

- [ ]* 13.4 Write unit tests for ClerkProvider setup
  - Test ClerkProvider wrapping
  - Test publishable key configuration
  - Test configuration error display when key missing

- [x] 14. Create authenticated API client utility
  - [x] 14.1 Implement createApiClient function
    - Create `devshowcase_frontend/src/utils/api.js`
    - Accept getToken function as parameter
    - Implement request method with token injection
    - Add Authorization header with Bearer token format
    - Implement convenience methods (get, post, put, patch, delete)
    - _Requirements: 2.3, 2.4, 2.5_
  
  - [x] 14.2 Create useApi custom hook
    - Use useAuth hook from Clerk to get getToken
    - Return API client instance with token injection
    - _Requirements: 2.3, 2.4_

- [ ]* 14.3 Write property tests for API client
  - **Property 4: API Request Token Injection** - Validates: Requirements 2.4

- [ ]* 14.4 Write unit tests for API client
  - Test token injection in requests
  - Test request methods (get, post, put, patch, delete)
  - Test header merging
  - Test error handling

- [ ] 15. Update authentication context and components
  - [ ] 15.1 Update Login page component
    - Replace existing login form with Clerk SignIn component
    - Handle authentication state from useAuth hook
    - Redirect to dashboard on successful sign-in
    - _Requirements: 2.3, 2.7_
  
  - [ ] 15.2 Update navigation/header components
    - Use useAuth hook to get authentication state
    - Display user info when signed in
    - Add sign-out button using Clerk's signOut method
    - Handle loading state while auth status is determined
    - _Requirements: 2.6, 2.7, 2.8_
  
  - [ ] 15.3 Update protected route logic
    - Use isSignedIn from useAuth hook
    - Redirect to login if not authenticated
    - Show loading state while isLoaded is false
    - _Requirements: 2.7, 2.8_

- [ ]* 15.4 Write unit tests for authentication components
  - Test sign-in flow
  - Test sign-out cleanup
  - Test loading state display
  - Test auth state propagation
  - Test protected route redirects

- [x] 16. Implement sandbox generation UI in project editor
  - [x] 16.1 Add sandbox generation button
    - Add button to project editor (OverviewTab or similar)
    - Only show button to authenticated project owners
    - Disable button if sandbox already exists
    - _Requirements: 8.1, 8.6_
  
  - [x] 16.2 Implement sandbox generation handler
    - Call POST /api/sandbox/generate/<project_id>/ using authenticated API client
    - Show loading state during generation
    - Display success message on completion
    - Display error message on failure
    - Update project state to reflect sandbox exists
    - _Requirements: 8.2, 8.3, 8.4_
  
  - [x] 16.3 Add sandbox status indicator
    - Display badge/indicator when sandbox is active
    - Show in project editor and API playground
    - _Requirements: 8.5_

- [ ]* 16.4 Write unit tests for sandbox UI
  - Test button visibility for owners vs. non-owners
  - Test button click triggers API call
  - Test success message display
  - Test error message display
  - Test sandbox active indicator

- [-] 17. Update API playground to show execution mode
  - [x] 17.1 Update execution response display
    - Show "mode" field from response (sandbox or proxy)
    - Add visual indicator for sandbox mode
    - Display appropriate messaging for each mode
    - _Requirements: 4.10_
  
  - [x] 17.2 Update API client calls in playground
    - Use authenticated API client from useApi hook
    - Ensure JWT token is included in execution requests
    - _Requirements: 2.4_

- [ ]* 17.3 Write unit tests for API playground updates
  - Test mode indicator display
  - Test sandbox vs. proxy visual differences
  - Test authenticated request execution

- [ ] 18. Update all API calls to use authenticated client
  - Replace fetch calls with authenticated API client throughout the app
  - Update project creation, editing, deletion endpoints
  - Update endpoint management API calls
  - Ensure backward compatibility with existing functionality
  - _Requirements: 2.4, 2.5_

- [ ] 19. Final checkpoint - End-to-end integration test
  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 20. Write integration tests for complete flows
  - Test end-to-end: sign in → create project → generate sandbox → execute endpoint
  - Test sandbox mode indicator in API playground
  - Test proxy mode fallback when no sandbox
  - Test authorization across the stack
  - Test rate limiting behavior

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples, edge cases, and integration points
- The implementation follows a bottom-up approach: authentication → models → service → views → frontend
- All backend code is Python/Django, all frontend code is JavaScript/React
- Existing partial implementations should be completed rather than rewritten
- The sandbox app needs to be added to INSTALLED_APPS and URLs need to be registered
- Frontend requires @clerk/clerk-react package installation
- Environment variables must be configured for both backend (CLERK_DOMAIN, CLERK_AUDIENCE) and frontend (VITE_CLERK_PUBLISHABLE_KEY)
