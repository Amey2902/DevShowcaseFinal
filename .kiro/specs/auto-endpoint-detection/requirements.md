# Requirements Document

## Introduction

The Auto-Endpoint Detection feature enables users to upload their project folders as zip files, automatically analyze the code to detect API endpoints, extract endpoint details, and generate documentation. The system provides sandbox mode for public users to test endpoints with mock data, while project owners can test with live API calls. The feature leverages Groq AI for intelligent code analysis and supports multiple programming languages and frameworks.

## Glossary

- **Project_Owner**: A user who has uploaded and owns a project in the system
- **Public_User**: A user who can view and interact with projects but does not own them
- **Endpoint**: An API route with an HTTP method, path, parameters, and request/response schema
- **Sandbox_Mode**: A testing environment where endpoints execute with simulated mock data
- **Live_Mode**: A testing environment where endpoints execute with real API calls
- **Upload_Service**: The component responsible for handling zip file uploads
- **Analysis_Engine**: The component that uses Groq AI to analyze code and detect endpoints
- **Endpoint_Extractor**: The component that parses code to extract endpoint details
- **Security_Scanner**: The component that validates and scans uploaded files for malicious code
- **Documentation_Generator**: The component that creates endpoint documentation from extracted data
- **Execution_Service**: The component that handles endpoint testing in sandbox or live mode

## Requirements

### Requirement 1: Upload Project Files

**User Story:** As a Project_Owner, I want to upload my project folder as a zip file or provide a GitHub repository URL, so that the system can analyze my API endpoints regardless of project size.

#### Acceptance Criteria

1. WHEN a Project_Owner uploads a zip file, THE Upload_Service SHALL accept files up to 100MB in size
2. WHEN a zip file is uploaded, THE Upload_Service SHALL extract the contents to a secure temporary directory
3. IF the uploaded file is not a valid zip file, THEN THE Upload_Service SHALL return an error message indicating invalid file format
4. IF the uploaded file exceeds 100MB, THEN THE Upload_Service SHALL suggest using GitHub repository URL instead
5. WHEN a Project_Owner provides a GitHub repository URL, THE Upload_Service SHALL clone the repository to a secure temporary directory
6. WHEN using GitHub URL, THE Upload_Service SHALL support both public and private repositories (with access token)
7. IF the GitHub repository cannot be accessed, THEN THE Upload_Service SHALL return an error message indicating repository access failed
8. WHEN a zip file or repository is successfully processed, THE Upload_Service SHALL return a unique upload identifier

### Requirement 2: Validate Uploaded Files

**User Story:** As a system administrator, I want uploaded files to be validated and scanned for security threats, so that malicious code cannot compromise the system.

#### Acceptance Criteria

1. WHEN a zip file is extracted, THE Security_Scanner SHALL validate that the archive contains only allowed file types
2. WHEN validating file types, THE Security_Scanner SHALL reject executable files, scripts with dangerous patterns, and binary files outside allowed types
3. WHEN scanning files, THE Security_Scanner SHALL detect common malicious patterns including shell commands, file system operations, and network calls
4. IF malicious code is detected, THEN THE Security_Scanner SHALL delete the uploaded files and return a security violation error
5. WHEN validation passes, THE Security_Scanner SHALL mark the upload as safe for analysis

### Requirement 3: Analyze Code with AI

**User Story:** As a Project_Owner, I want the system to automatically analyze my code using AI, so that endpoints can be detected without manual configuration.

#### Acceptance Criteria

1. WHEN an upload is marked safe, THE Analysis_Engine SHALL send the project structure and relevant code files to Groq AI
2. WHEN analyzing code, THE Analysis_Engine SHALL identify the programming language and framework used
3. WHEN the framework is identified, THE Analysis_Engine SHALL detect all API endpoint definitions in the codebase
4. THE Analysis_Engine SHALL support Express, Flask, Django, FastAPI, Spring Boot, and ASP.NET frameworks
5. WHEN analysis completes, THE Analysis_Engine SHALL return a list of detected endpoints with their file locations

### Requirement 4: Extract Endpoint Details

**User Story:** As a Project_Owner, I want endpoint details to be automatically extracted, so that I have complete documentation without manual effort.

#### Acceptance Criteria

1. WHEN an endpoint is detected, THE Endpoint_Extractor SHALL extract the HTTP method (GET, POST, PUT, DELETE, PATCH)
2. WHEN an endpoint is detected, THE Endpoint_Extractor SHALL extract the URL path including path parameters
3. WHEN an endpoint is detected, THE Endpoint_Extractor SHALL extract query parameters with their types and descriptions
4. WHEN an endpoint is detected, THE Endpoint_Extractor SHALL extract request body schema if applicable
5. WHEN an endpoint is detected, THE Endpoint_Extractor SHALL extract response schema including status codes and response bodies
6. WHEN an endpoint is detected, THE Endpoint_Extractor SHALL extract authentication requirements if specified
7. WHEN extraction completes, THE Endpoint_Extractor SHALL store all endpoint details in the database

### Requirement 5: Generate Endpoint Documentation

**User Story:** As a Project_Owner, I want automatic documentation for my endpoints, so that other users can understand how to use my API.

#### Acceptance Criteria

1. WHEN endpoint details are extracted, THE Documentation_Generator SHALL create a formatted documentation page for each endpoint
2. WHEN generating documentation, THE Documentation_Generator SHALL include the HTTP method, path, description, parameters, request schema, and response schema
3. WHEN generating documentation, THE Documentation_Generator SHALL include example requests and responses
4. WHEN documentation is generated, THE Documentation_Generator SHALL make it accessible to both Project_Owner and Public_User
5. THE Documentation_Generator SHALL format documentation in a human-readable structure

### Requirement 6: Execute Endpoints in Sandbox Mode

**User Story:** As a Public_User, I want to test API endpoints with mock data, so that I can understand how the API works without affecting real data.

#### Acceptance Criteria

1. WHEN a Public_User requests to test an endpoint, THE Execution_Service SHALL execute the endpoint in Sandbox_Mode
2. WHILE in Sandbox_Mode, THE Execution_Service SHALL use mock data instead of making real API calls
3. WHEN executing in Sandbox_Mode, THE Execution_Service SHALL generate realistic mock responses based on the response schema
4. WHEN a Public_User attempts to switch to Live_Mode, THE Execution_Service SHALL deny the request with an authorization error
5. WHEN execution completes, THE Execution_Service SHALL return the mock response to the Public_User

### Requirement 7: Execute Endpoints in Live Mode

**User Story:** As a Project_Owner, I want to test my endpoints with real API calls, so that I can verify they work correctly with actual data.

#### Acceptance Criteria

1. WHEN a Project_Owner requests to test an endpoint, THE Execution_Service SHALL allow selection between Sandbox_Mode and Live_Mode
2. WHEN a Project_Owner selects Live_Mode, THE Execution_Service SHALL execute the endpoint with real API calls
3. WHILE in Live_Mode, THE Execution_Service SHALL use the actual backend services and databases
4. IF an error occurs during Live_Mode execution, THEN THE Execution_Service SHALL return the actual error response
5. WHEN execution completes, THE Execution_Service SHALL return the real response to the Project_Owner

### Requirement 8: Manage Endpoint Permissions

**User Story:** As a Project_Owner, I want to control who can access my endpoints in different modes, so that I can protect my live data while allowing public testing.

#### Acceptance Criteria

1. WHEN an endpoint is created, THE Execution_Service SHALL set the Project_Owner as the only user authorized for Live_Mode
2. WHEN an endpoint is created, THE Execution_Service SHALL allow all users to access Sandbox_Mode
3. WHEN a user requests endpoint execution, THE Execution_Service SHALL verify the user's authorization level
4. IF a Public_User attempts Live_Mode access, THEN THE Execution_Service SHALL return an authorization error
5. WHEN a Project_Owner views their project, THE Execution_Service SHALL display both Sandbox_Mode and Live_Mode options

### Requirement 9: Handle Multiple Programming Languages

**User Story:** As a Project_Owner, I want to upload projects in different programming languages, so that I can showcase APIs regardless of the technology stack.

#### Acceptance Criteria

1. WHEN analyzing code, THE Analysis_Engine SHALL detect Python, JavaScript, TypeScript, Java, and C# languages
2. WHEN the language is Python, THE Endpoint_Extractor SHALL parse Flask, Django, and FastAPI endpoint definitions
3. WHEN the language is JavaScript or TypeScript, THE Endpoint_Extractor SHALL parse Express and NestJS endpoint definitions
4. WHEN the language is Java, THE Endpoint_Extractor SHALL parse Spring Boot endpoint definitions
5. WHEN the language is C#, THE Endpoint_Extractor SHALL parse ASP.NET endpoint definitions
6. IF the language or framework is not supported, THEN THE Analysis_Engine SHALL return an error indicating unsupported technology

### Requirement 10: Store and Retrieve Endpoint Data

**User Story:** As a Project_Owner, I want my endpoint data to be persisted, so that I don't need to re-upload and re-analyze my project every time.

#### Acceptance Criteria

1. WHEN endpoint extraction completes, THE Endpoint_Extractor SHALL store all endpoint data in the database associated with the project
2. WHEN a Project_Owner views their project, THE Execution_Service SHALL retrieve all stored endpoints from the database
3. WHEN a Project_Owner updates their project, THE Upload_Service SHALL allow re-uploading and re-analyzing the code
4. WHEN re-analysis occurs, THE Endpoint_Extractor SHALL update existing endpoints and add new ones
5. WHEN a Project_Owner deletes their project, THE Execution_Service SHALL delete all associated endpoint data

### Requirement 11: Provide Upload Progress Feedback

**User Story:** As a Project_Owner, I want to see the progress of my upload and analysis, so that I know the system is working and how long to wait.

#### Acceptance Criteria

1. WHEN a file upload begins, THE Upload_Service SHALL provide upload progress percentage
2. WHEN file extraction begins, THE Upload_Service SHALL indicate extraction is in progress
3. WHEN security scanning begins, THE Security_Scanner SHALL indicate scanning is in progress
4. WHEN AI analysis begins, THE Analysis_Engine SHALL indicate analysis is in progress
5. WHEN endpoint extraction begins, THE Endpoint_Extractor SHALL indicate extraction is in progress
6. WHEN all steps complete, THE Upload_Service SHALL indicate completion with the number of endpoints detected

### Requirement 12: Handle Analysis Errors Gracefully

**User Story:** As a Project_Owner, I want clear error messages when analysis fails, so that I can understand what went wrong and how to fix it.

#### Acceptance Criteria

1. IF the Analysis_Engine cannot determine the framework, THEN THE Analysis_Engine SHALL return an error message indicating the framework could not be detected
2. IF the Endpoint_Extractor finds no endpoints, THEN THE Endpoint_Extractor SHALL return a message indicating no endpoints were found
3. IF Groq AI service is unavailable, THEN THE Analysis_Engine SHALL return an error indicating the AI service is temporarily unavailable
4. IF file parsing fails, THEN THE Endpoint_Extractor SHALL return an error indicating which files could not be parsed
5. WHEN an error occurs, THE Upload_Service SHALL preserve the uploaded files for retry or manual review

