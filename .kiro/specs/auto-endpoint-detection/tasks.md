# Implementation Plan: Auto-Endpoint Detection

## Overview

This implementation plan breaks down the Auto-Endpoint Detection feature into discrete, actionable coding tasks. The feature enables users to upload project files (zip or GitHub URL), automatically analyze code using Groq AI to detect API endpoints, extract endpoint details, and generate interactive documentation with sandbox testing capabilities.

The implementation follows a layered approach: data models → core services → API endpoints → frontend components → integration → testing.

## Tasks

- [x] 1. Set up data models and database migrations
  - [x] 1.1 Create ProjectUpload model with status tracking
    - Add model to `devshowcase_backend/projects/models.py`
    - Include fields: id (UUID), project (FK), user (FK), upload_method, github_url, file_size, status, progress_percentage, current_message, detected_language, detected_framework, endpoints_found, error_message, created_at, completed_at, temp_directory
    - Add STATUS_CHOICES for tracking pipeline stages
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_
  
  - [x] 1.2 Extend Endpoint model with auto-detection fields
    - Add fields to existing Endpoint model: detected_from_file, detected_at_line, path_parameters (JSONField), query_parameters (JSONField), auth_required, auth_type, request_schema (JSONField), response_schema (JSONField), auto_detected
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_
  
  - [x] 1.3 Create and run database migrations
    - Generate migrations with `python manage.py makemigrations`
    - Review migration files for correctness
    - _Requirements: 10.1_
  
  - [x] 1.4 Update serializers for new models
    - Create ProjectUploadSerializer in `devshowcase_backend/projects/serializers.py`
    - Update EndpointSerializer to include new auto-detection fields
    - _Requirements: 10.2_

- [x] 2. Implement Upload Service
  - [x] 2.1 Create UploadService class with file handling
    - Create `devshowcase_backend/projects/services/upload_service.py`
    - Implement `handle_zip_upload()` method to accept and extract zip files
    - Implement `handle_github_url()` method to clone repositories
    - Implement `get_upload_status()` method for progress tracking
    - Add file size validation (100MB limit for zip, 500MB for GitHub)
    - Create secure temporary directories with proper permissions
    - _Requirements: 1.1, 1.2, 1.4, 1.5, 1.8_
  
  - [ ]* 2.2 Write unit tests for UploadService
    - Test zip file extraction with valid files
    - Test file size validation (under/over 100MB)
    - Test GitHub URL cloning with public repos
    - Test error handling for invalid formats
    - _Requirements: 1.3, 1.7_
  
  - [ ]* 2.3 Write property test for file size validation
    - **Property 1: File Size Validation**
    - **Validates: Requirements 1.1, 1.4**

- [x] 3. Implement Security Scanner
  - [x] 3.1 Create SecurityScanner class with validation logic
    - Create `devshowcase_backend/projects/services/security_scanner.py`
    - Define ALLOWED_EXTENSIONS constant with safe file types
    - Define FORBIDDEN_PATTERNS list with malicious code patterns
    - Implement `scan_directory()` method to scan all extracted files
    - Implement `validate_file_type()` method for extension checking
    - Implement path traversal prevention in extraction
    - Add cleanup logic for unsafe uploads
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ]* 3.2 Write unit tests for SecurityScanner
    - Test allowed file type validation
    - Test malicious pattern detection (os.system, eval, exec)
    - Test path traversal prevention
    - Test cleanup of unsafe files
    - _Requirements: 2.3, 2.4_
  
  - [ ]* 3.3 Write property test for file type validation
    - **Property 7: File Type Allowlist Validation**
    - **Validates: Requirements 2.1, 2.2**

- [x] 4. Implement Analysis Engine with Groq AI integration
  - [x] 4.1 Create AnalysisEngine class with AI integration
    - Create `devshowcase_backend/projects/services/analysis_engine.py`
    - Define SUPPORTED_FRAMEWORKS dictionary
    - Implement `analyze_project()` method to coordinate AI analysis
    - Implement `build_ai_prompt()` to construct prompts for Groq AI
    - Implement `parse_ai_response()` to extract endpoint locations from AI response
    - Add retry logic with exponential backoff for AI calls
    - Add timeout handling (30 seconds per request)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 4.2 Implement Groq AI client wrapper
    - Create helper function `call_groq_ai_safely()` with safety measures
    - Add prompt sanitization to prevent injection
    - Add response validation before parsing
    - Use existing GROQ_API_KEY from settings
    - _Requirements: 3.1_
  
  - [ ]* 4.3 Write unit tests for AnalysisEngine
    - Test language detection for Python, JavaScript, TypeScript, Java, C#
    - Test framework detection for Flask, Django, FastAPI, Express, Spring Boot
    - Test AI prompt construction
    - Test AI response parsing
    - Test error handling for unsupported languages
    - _Requirements: 3.2, 9.1, 9.6_
  
  - [ ]* 4.4 Write property test for language detection
    - **Property 12: Language and Framework Detection**
    - **Validates: Requirements 3.2**

- [ ] 5. Checkpoint - Ensure core services are working
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement Endpoint Extractor
  - [x] 6.1 Create EndpointExtractor class with parsing logic
    - Create `devshowcase_backend/projects/services/endpoint_extractor.py`
    - Implement `extract_endpoint_details()` method as main entry point
    - Implement framework-specific parsers: `parse_flask_endpoint()`, `parse_django_endpoint()`, `parse_fastapi_endpoint()`, `parse_express_endpoint()`, `parse_react_api_calls()`, `parse_spring_boot_endpoint()`, `parse_aspnet_endpoint()`
    - Extract HTTP methods, URL paths, path parameters, query parameters
    - Extract request/response schemas using AST parsing or regex
    - Detect authentication requirements from decorators/middleware
    - For React: detect fetch/axios calls and extract API endpoints being called
    - Implement `save_endpoints()` method to persist to database
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 9.2, 9.3, 9.4, 9.5_
  
  - [ ]* 6.2 Write unit tests for EndpointExtractor
    - Test Flask route parsing with path parameters
    - Test Django URL pattern parsing
    - Test Express route parsing
    - Test request/response schema extraction
    - Test authentication detection
    - Test database persistence
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
  
  - [ ]* 6.3 Write property test for endpoint persistence
    - **Property 21: Endpoint Data Persistence**
    - **Validates: Requirements 4.7, 10.1**

- [ ] 7. Implement Documentation Generator
  - [ ] 7.1 Create DocumentationGenerator class
    - Create `devshowcase_backend/projects/services/documentation_generator.py`
    - Implement `generate_endpoint_docs()` method to format documentation
    - Implement `generate_example_request()` to create realistic examples
    - Implement `generate_example_response()` based on response schema
    - Generate curl commands for each endpoint
    - Format parameters into readable tables
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 7.2 Write unit tests for DocumentationGenerator
    - Test documentation formatting
    - Test example request generation
    - Test example response generation
    - Test curl command generation
    - _Requirements: 5.2, 5.3_

- [x] 8. Implement API endpoints for upload and analysis
  - [x] 8.1 Create upload views
    - Create `upload_zip` view in `devshowcase_backend/projects/views.py`
    - Create `upload_github` view for GitHub URL uploads
    - Add authentication check (IsAuthenticated, project owner only)
    - Add rate limiting (5 uploads/hour for zip, 10/hour for GitHub)
    - Return 202 Accepted with upload_id
    - _Requirements: 1.1, 1.5, 1.8_
  
  - [x] 8.2 Create status tracking view
    - Create `upload_status` view to return current progress
    - Include status, progress percentage, message, endpoints_found
    - Add ownership verification
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_
  
  - [x] 8.3 Create endpoint retrieval view
    - Create or update view to return detected endpoints for a project
    - Include all auto-detection fields in response
    - Allow public access for published projects
    - _Requirements: 10.2_
  
  - [x] 8.4 Create retry and delete views
    - Create `upload_retry` view to retry failed uploads
    - Create `upload_delete` view to delete upload records
    - _Requirements: 12.5_
  
  - [x] 8.5 Add URL patterns
    - Add URL patterns to `devshowcase_backend/projects/urls.py`
    - Map: `/projects/<id>/upload/zip/`, `/projects/<id>/upload/github/`, `/uploads/<uuid>/status/`, `/uploads/<uuid>/retry/`, `/uploads/<uuid>/`
    - _Requirements: 1.1, 1.5_
  
  - [ ]* 8.6 Write integration tests for API endpoints
    - Test complete upload → scan → analyze → extract flow
    - Test status polling during analysis
    - Test endpoint retrieval after completion
    - Test error responses for invalid uploads
    - _Requirements: 1.1, 1.3, 1.7, 2.4, 3.5_

- [x] 9. Implement background task orchestration
  - [x] 9.1 Create async task coordinator
    - Create `devshowcase_backend/projects/tasks.py` for background processing
    - Implement `process_upload_pipeline()` function to orchestrate: extract → scan → analyze → extract endpoints → generate docs
    - Update ProjectUpload status at each stage
    - Handle errors gracefully and update error_message field
    - Clean up temporary files after completion
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [x] 9.2 Integrate task coordinator with upload views
    - Call `process_upload_pipeline()` from upload views
    - Use threading or async execution to avoid blocking
    - _Requirements: 1.8_
  
  - [ ]* 9.3 Write integration tests for pipeline
    - Test complete pipeline with sample Flask project
    - Test complete pipeline with sample Express project
    - Test error handling at each stage
    - Test progress updates throughout pipeline
    - _Requirements: 11.6, 12.1, 12.2, 12.3, 12.4_

- [ ] 10. Checkpoint - Ensure backend is complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement frontend upload component
  - [x] 11.1 Create ProjectUpload component
    - Create `devshowcase_frontend/src/components/ProjectUpload.jsx`
    - Add file upload input with drag-and-drop support
    - Add GitHub URL input field with optional access token
    - Add upload method toggle (zip vs GitHub)
    - Implement file upload with progress tracking
    - Show file size validation errors
    - _Requirements: 1.1, 1.4, 1.5_
  
  - [x] 11.2 Add upload API integration
    - Create API client functions in `devshowcase_frontend/src/api/projects.js`
    - Implement `uploadZipFile()` function
    - Implement `uploadGithubUrl()` function
    - Handle multipart/form-data for file uploads
    - _Requirements: 1.1, 1.5_

- [x] 12. Implement frontend progress tracker
  - [x] 12.1 Create AnalysisProgress component
    - Create `devshowcase_frontend/src/components/AnalysisProgress.jsx`
    - Display progress bar with percentage
    - Show current stage (uploading, extracting, scanning, analyzing, extracting_endpoints, complete)
    - Show status messages
    - Poll status API every 2 seconds during processing
    - Display endpoints_found count when complete
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_
  
  - [x] 12.2 Add status polling logic
    - Implement `pollUploadStatus()` function
    - Stop polling when status is 'completed' or 'failed'
    - Handle errors and display error messages
    - _Requirements: 11.6, 12.1, 12.2, 12.3, 12.4_

- [ ] 13. Implement frontend endpoint display
  - [ ] 13.1 Update endpoint list component
    - Update existing endpoint display to show auto-detected endpoints
    - Display detected_from_file and detected_at_line for auto-detected endpoints
    - Show path_parameters and query_parameters in documentation
    - Display auth_required badge
    - Format request_schema and response_schema
    - _Requirements: 5.2, 5.3, 5.4_
  
  - [ ] 13.2 Add endpoint documentation viewer
    - Create or update component to display formatted documentation
    - Show example requests and responses
    - Display curl commands
    - Show parameters table
    - _Requirements: 5.2, 5.3, 5.5_

- [ ] 14. Implement execution mode controls
  - [ ] 14.1 Add sandbox/live mode toggle
    - Update API playground component to show mode selector
    - Show sandbox mode only for non-owners
    - Show both modes for project owners
    - Add visual indicator for current mode
    - _Requirements: 6.1, 7.1, 8.1, 8.5_
  
  - [ ] 14.2 Implement mode-based execution
    - Update execution logic to pass selected mode to backend
    - Handle authorization errors for non-owners attempting live mode
    - Display mock data indicator in sandbox mode
    - _Requirements: 6.2, 6.4, 7.2, 8.4_
  
  - [ ]* 14.3 Write property test for sandbox enforcement
    - **Property 25: Public User Sandbox Enforcement**
    - **Validates: Requirements 6.1, 6.2, 6.4, 8.4**

- [x] 15. Integrate upload flow into project creation/editing
  - [x] 15.1 Add upload section to project edit page
    - Update `devshowcase_frontend/src/pages/ProjectEdit.jsx`
    - Add ProjectUpload component
    - Add AnalysisProgress component
    - Show upload history for the project
    - _Requirements: 1.1, 1.5_
  
  - [x] 15.2 Add re-analysis functionality
    - Add "Re-analyze" button for existing projects
    - Show confirmation dialog before re-analysis
    - Display updated endpoint count after re-analysis
    - _Requirements: 10.3, 10.4_

- [ ] 16. Implement temporary file cleanup
  - [ ] 16.1 Create cleanup management command
    - Create `devshowcase_backend/projects/management/commands/cleanup_temp_files.py`
    - Implement logic to delete temp directories older than 24 hours
    - Update ProjectUpload records to clear temp_directory field
    - _Requirements: 12.5_
  
  - [ ] 16.2 Add cleanup to task pipeline
    - Call cleanup after successful or failed analysis
    - Ensure files are deleted even on errors
    - _Requirements: 12.5_

- [ ] 17. Add error handling and user feedback
  - [ ] 17.1 Implement comprehensive error messages
    - Add error message display in upload component
    - Show specific errors for: file too large, invalid format, security violation, unsupported framework, no endpoints found, AI service unavailable
    - Add retry button for failed uploads
    - _Requirements: 12.1, 12.2, 12.3, 12.4_
  
  - [ ] 17.2 Add success notifications
    - Show success message with endpoint count on completion
    - Add link to view detected endpoints
    - _Requirements: 11.6_

- [ ] 18. Final checkpoint - End-to-end testing
  - [ ] 18.1 Test complete user flows
    - Test: Upload Flask project zip → View detected endpoints → Test in sandbox
    - Test: Upload Express project via GitHub → View documentation → Test in live mode (as owner)
    - Test: Public user views project → Tests endpoint in sandbox only
    - Test: Re-upload project → Verify endpoints updated
    - Test: Upload project with security violation → Verify rejection
    - Test: Upload unsupported framework → Verify error message
  
  - [ ] 18.2 Verify all requirements are met
    - Review requirements document and verify each acceptance criterion
    - Test edge cases and error conditions
    - Verify performance benchmarks (upload < 5s, analysis < 60s)
  
  - [ ] 18.3 Final cleanup and documentation
    - Ensure all temporary files are cleaned up
    - Verify database migrations are applied
    - Test with multiple concurrent uploads
    - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- The implementation uses Python/Django for backend and React for frontend
- Groq AI integration uses existing configuration from settings.py
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples and integration points
- Checkpoints ensure incremental validation at key milestones
- Background task processing can use threading initially, migrate to Celery if needed for production
- Security is paramount: all uploads are scanned before analysis
- Temporary files are automatically cleaned up after 24 hours
