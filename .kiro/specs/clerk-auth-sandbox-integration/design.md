# Design Document: Clerk Authentication and Sandbox Mode Integration

## Overview

This design document specifies the technical implementation for integrating Clerk JWT authentication and implementing isolated sandbox environments in the DevShowcase platform. The solution replaces the existing DRF Token authentication with a hybrid authentication system that supports both Clerk JWT and legacy DRF tokens, while adding a complete sandbox execution engine that allows users to test API endpoints without calling external APIs or modifying real data.

### Goals

1. Implement Clerk JWT authentication with RS256 signature verification
2. Maintain backward compatibility with existing DRF Token authentication
3. Create isolated sandbox environments for testing API endpoints
4. Implement a hybrid execution engine that routes requests to sandbox or proxy
5. Enforce authentication-based authorization for write operations
6. Apply rate limiting to prevent abuse
7. Ensure complete data isolation between sandbox and production systems

### Non-Goals

1. Migrating existing user accounts to Clerk (users will create new accounts)
2. Implementing sandbox data persistence across sessions (sandbox data is ephemeral)
3. Supporting complex query parameters or filtering in sandbox mode
4. Implementing real-time synchronization between sandbox and external APIs
5. Providing sandbox data export/import functionality

## Architecture

### High-Level Architecture

The system consists of three main architectural layers:

1. **Authentication Layer**: Handles JWT validation and user identity management
2. **Execution Layer**: Routes requests between sandbox and proxy modes
3. **Sandbox Layer**: Manages isolated data environments and request execution

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ ClerkProvider│  │ API Playground│  │ Project Editor│      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │               │
│         └──────────────────┴──────────────────┘               │
│                            │                                  │
│                    Bearer JWT Token                           │
└────────────────────────────┼──────────────────────────────────┘
                             │
┌────────────────────────────┼──────────────────────────────────┐
│                    Backend (Django)                           │
│                            │                                  │
│  ┌─────────────────────────▼────────────────────────┐        │
│  │      Authentication Middleware                    │        │
│  │  ┌──────────────────┐  ┌──────────────────┐     │        │
│  │  │ClerkAuthentication│→│TokenAuthentication│     │        │
│  │  └──────────────────┘  └──────────────────┘     │        │
│  └─────────────────────────┬────────────────────────┘        │
│                            │                                  │
│  ┌─────────────────────────▼────────────────────────┐        │
│  │         Execution View (Rate Limited)             │        │
│  │  ┌──────────────────────────────────────┐        │        │
│  │  │  Check Authentication & Permissions  │        │        │
│  │  └──────────────┬───────────────────────┘        │        │
│  │                 │                                 │        │
│  │     ┌───────────▼──────────┐                     │        │
│  │     │ Sandbox Exists?      │                     │        │
│  │     └───┬──────────────┬───┘                     │        │
│  │         │ Yes          │ No                      │        │
│  │         │              │                         │        │
│  │  ┌──────▼──────┐  ┌───▼──────┐                  │        │
│  │  │   Sandbox   │  │  Proxy   │                  │        │
│  │  │   Service   │  │  Service │                  │        │
│  │  └──────┬──────┘  └───┬──────┘                  │        │
│  │         │              │                         │        │
│  │         │              │                         │        │
│  │  ┌──────▼──────────────▼──────┐                 │        │
│  │  │   Unified Response Format   │                 │        │
│  │  └─────────────────────────────┘                 │        │
│  └──────────────────────────────────────────────────┘        │
│                                                               │
│  ┌────────────────────────────────────────────────┐          │
│  │           Sandbox Data Layer                   │          │
│  │  ┌──────────────────┐                          │          │
│  │  │SandboxEnvironment│                          │          │
│  │  └────────┬─────────┘                          │          │
│  │           │ 1:N                                │          │
│  │  ┌────────▼─────────┐                          │          │
│  │  │SandboxCollection │                          │          │
│  │  └────────┬─────────┘                          │          │
│  │           │ 1:N                                │          │
│  │  ┌────────▼─────────┐                          │          │
│  │  │  SandboxRecord   │                          │          │
│  │  └──────────────────┘                          │          │
│  └────────────────────────────────────────────────┘          │
└───────────────────────────────────────────────────────────────┘
                             │
                             │ HTTP Proxy
                             │
┌────────────────────────────▼──────────────────────────────────┐
│                    External APIs                              │
└───────────────────────────────────────────────────────────────┘
```

### Authentication Flow

```
┌──────┐                ┌──────────┐              ┌────────┐
│Client│                │  Django  │              │ Clerk  │
└──┬───┘                └────┬─────┘              └───┬────┘
   │                         │                        │
   │ 1. Request with Bearer  │                        │
   │    JWT Token            │                        │
   ├────────────────────────►│                        │
   │                         │                        │
   │                         │ 2. Fetch JWKS          │
   │                         ├───────────────────────►│
   │                         │                        │
   │                         │ 3. Return Public Keys  │
   │                         │◄───────────────────────┤
   │                         │                        │
   │                         │ 4. Verify JWT          │
   │                         │    Signature (RS256)   │
   │                         │                        │
   │                         │ 5. Extract user_id     │
   │                         │    from 'sub' claim    │
   │                         │                        │
   │                         │ 6. Get or Create User  │
   │                         │                        │
   │ 7. Authenticated        │                        │
   │    Response             │                        │
   │◄────────────────────────┤                        │
   │                         │                        │
```

### Sandbox Execution Flow

```
┌──────┐              ┌──────────┐              ┌─────────┐
│Client│              │Execution │              │ Sandbox │
│      │              │   View   │              │ Service │
└──┬───┘              └────┬─────┘              └────┬────┘
   │                       │                         │
   │ 1. Execute Endpoint   │                         │
   ├──────────────────────►│                         │
   │                       │                         │
   │                       │ 2. Check Auth           │
   │                       │    & Permissions        │
   │                       │                         │
   │                       │ 3. Check Sandbox        │
   │                       │    Exists?              │
   │                       │                         │
   │                       │ 4. Execute in Sandbox   │
   │                       ├────────────────────────►│
   │                       │                         │
   │                       │                         │ 5. Parse URL
   │                       │                         │    Extract Resource
   │                       │                         │
   │                       │                         │ 6. Find Collection
   │                       │                         │
   │                       │                         │ 7. Execute CRUD
   │                       │                         │    Operation
   │                       │                         │
   │                       │ 8. Return Response      │
   │                       │◄────────────────────────┤
   │                       │                         │
   │ 9. Unified Response   │                         │
   │◄──────────────────────┤                         │
   │                       │                         │
```

## Components and Interfaces

### 1. ClerkAuthentication Class

**Location**: `accounts/authentication.py`

**Purpose**: Validates Clerk JWT tokens and creates/retrieves Django users

**Interface**:
```python
class ClerkAuthentication(BaseAuthentication):
    """
    Custom DRF authentication class that validates Clerk JWT tokens.
    Falls back to None if Bearer token is not present, allowing
    other authentication classes to be tried.
    """
    
    @lru_cache(maxsize=1)
    def get_jwks(self) -> dict:
        """
        Fetches JWKS from Clerk domain.
        Cached to avoid repeated network calls.
        
        Returns:
            dict: JWKS response containing public keys
            
        Raises:
            requests.RequestException: If JWKS fetch fails
        """
        
    def authenticate(self, request) -> Optional[Tuple[User, None]]:
        """
        Authenticates request using Clerk JWT token.
        
        Args:
            request: Django request object
            
        Returns:
            Tuple of (User, None) if authentication succeeds
            None if no Bearer token present (allows fallback)
            
        Raises:
            AuthenticationFailed: If token is invalid or expired
        """
```

**Configuration**:
- `CLERK_DOMAIN`: Environment variable for Clerk domain (e.g., "clerk.your-domain.com")
- `CLERK_AUDIENCE`: Environment variable for Clerk frontend API identifier
- Default values used if not configured

**Dependencies**:
- `PyJWT` library for JWT decoding and verification
- `requests` library for JWKS fetching
- `django.contrib.auth.models.User` for user management

### 2. Sandbox Models

**Location**: `sandbox/models.py`

**Purpose**: Store sandbox environment data in isolated collections

#### SandboxEnvironment Model

```python
class SandboxEnvironment(models.Model):
    """
    Represents an isolated sandbox environment for a project.
    One-to-one relationship with Project.
    """
    project = models.OneToOneField(
        Project, 
        on_delete=models.CASCADE, 
        related_name='sandbox'
    )
    created_at = models.DateTimeField(auto_now_add=True)
```

**Fields**:
- `project`: One-to-one link to Project model
- `created_at`: Timestamp of sandbox creation

**Relationships**:
- One-to-one with Project (cascade delete)
- One-to-many with SandboxCollection

#### SandboxCollection Model

```python
class SandboxCollection(models.Model):
    """
    Represents a named collection of records within a sandbox.
    Corresponds to a REST resource (e.g., "users", "expenses").
    """
    environment = models.ForeignKey(
        SandboxEnvironment, 
        on_delete=models.CASCADE, 
        related_name='collections'
    )
    name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ['environment', 'name']
```

**Fields**:
- `environment`: Foreign key to SandboxEnvironment
- `name`: Collection name (e.g., "users", "expenses")

**Constraints**:
- Unique together on (environment, name)

**Relationships**:
- Many-to-one with SandboxEnvironment (cascade delete)
- One-to-many with SandboxRecord

#### SandboxRecord Model

```python
class SandboxRecord(models.Model):
    """
    Represents an individual data record within a collection.
    Stores arbitrary JSON data.
    """
    collection = models.ForeignKey(
        SandboxCollection, 
        on_delete=models.CASCADE, 
        related_name='records'
    )
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Fields**:
- `collection`: Foreign key to SandboxCollection
- `data`: JSON field storing record data
- `created_at`: Timestamp of record creation
- `updated_at`: Timestamp of last update

**Relationships**:
- Many-to-one with SandboxCollection (cascade delete)

### 3. SandboxService

**Location**: `sandbox/service.py`

**Purpose**: Handles sandbox generation and request execution logic

**Interface**:

```python
class SandboxService:
    """
    Service layer for sandbox operations.
    Handles generation and execution logic.
    """
    
    @staticmethod
    def generate_sandbox(project: Project) -> SandboxEnvironment:
        """
        Generates or updates sandbox environment for a project.
        
        Process:
        1. Get or create SandboxEnvironment for project
        2. Extract resource names from endpoint URLs
        3. Create SandboxCollections for each resource
        4. Populate collections with sample response data
        5. Avoid duplicate records
        
        Args:
            project: Project instance to generate sandbox for
            
        Returns:
            SandboxEnvironment instance with populated collections
            
        Raises:
            ValueError: If project has no endpoints
        """
    
    @staticmethod
    def extract_resource_name(url: str) -> str:
        """
        Extracts REST resource name from URL path.
        
        Examples:
            "https://api.example.com/users" -> "users"
            "https://api.example.com/api/v1/expenses" -> "expenses"
            "https://api.example.com/users/123" -> "users"
            
        Args:
            url: Full endpoint URL
            
        Returns:
            Resource name (pluralized noun)
        """
    
    @staticmethod
    def execute_sandbox_request(
        environment: SandboxEnvironment,
        endpoint: Endpoint,
        method: str,
        custom_body: dict
    ) -> dict:
        """
        Executes a request against sandbox data.
        
        Process:
        1. Extract resource name from endpoint URL
        2. Find corresponding SandboxCollection
        3. Execute CRUD operation based on HTTP method
        4. Return structured response
        
        Args:
            environment: SandboxEnvironment instance
            endpoint: Endpoint instance being executed
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            custom_body: Request body data
            
        Returns:
            dict with keys: mode, status_code, data, error
            
        Raises:
            ValueError: If collection not found
        """
    
    @staticmethod
    def _handle_get(collection: SandboxCollection, url: str) -> dict:
        """
        Handles GET requests in sandbox mode.
        
        Logic:
        - If URL contains ID (e.g., /users/123), return single record
        - Otherwise, return all records in collection
        
        Args:
            collection: SandboxCollection to query
            url: Request URL
            
        Returns:
            dict with status_code and data
        """
    
    @staticmethod
    def _handle_post(
        collection: SandboxCollection, 
        body: dict
    ) -> dict:
        """
        Handles POST requests in sandbox mode.
        
        Logic:
        - Generate new ID for record
        - Merge body data with generated ID
        - Create new SandboxRecord
        - Return created record with 201 status
        
        Args:
            collection: SandboxCollection to add to
            body: Request body data
            
        Returns:
            dict with status_code 201 and created data
        """
    
    @staticmethod
    def _handle_put(
        collection: SandboxCollection,
        url: str,
        body: dict
    ) -> dict:
        """
        Handles PUT requests in sandbox mode.
        
        Logic:
        - Extract ID from URL
        - Find existing record
        - Replace record data with body
        - Return updated record with 200 status
        
        Args:
            collection: SandboxCollection to update
            url: Request URL containing record ID
            body: Request body data
            
        Returns:
            dict with status_code 200 and updated data
            dict with status_code 404 if record not found
        """
    
    @staticmethod
    def _handle_patch(
        collection: SandboxCollection,
        url: str,
        body: dict
    ) -> dict:
        """
        Handles PATCH requests in sandbox mode.
        
        Logic:
        - Extract ID from URL
        - Find existing record
        - Merge body data with existing data
        - Return updated record with 200 status
        
        Args:
            collection: SandboxCollection to update
            url: Request URL containing record ID
            body: Request body data
            
        Returns:
            dict with status_code 200 and updated data
            dict with status_code 404 if record not found
        """
    
    @staticmethod
    def _handle_delete(
        collection: SandboxCollection,
        url: str
    ) -> dict:
        """
        Handles DELETE requests in sandbox mode.
        
        Logic:
        - Extract ID from URL
        - Find and delete record
        - Return 204 No Content status
        
        Args:
            collection: SandboxCollection to delete from
            url: Request URL containing record ID
            
        Returns:
            dict with status_code 204 and no data
            dict with status_code 404 if record not found
        """
    
    @staticmethod
    def _extract_id_from_url(url: str) -> Optional[int]:
        """
        Extracts numeric ID from URL path.
        
        Examples:
            "/users/123" -> 123
            "/api/expenses/456" -> 456
            "/users" -> None
            
        Args:
            url: URL path
            
        Returns:
            Numeric ID if found, None otherwise
        """
```

### 4. Execution View (Modified)

**Location**: `execution/views.py`

**Purpose**: Routes requests to sandbox or proxy based on availability

**Interface**:

```python
@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='10/m', method='POST')
def execute_endpoint(request):
    """
    Executes an API endpoint request.
    
    Flow:
    1. Validate endpoint_id and retrieve endpoint
    2. Check if project is published
    3. Check authentication for write operations
    4. Check if sandbox exists for project
    5. Route to sandbox or proxy
    6. Return unified response format
    
    Request Body:
        {
            "endpoint_id": int,
            "custom_body": dict (optional)
        }
        
    Response Format:
        {
            "mode": "sandbox" | "proxy",
            "status_code": int,
            "data": any,
            "error": str | null
        }
        
    Status Codes:
        200: Success (actual status in response body)
        400: Bad request (missing endpoint_id)
        403: Forbidden (unpublished project or unauthorized write)
        404: Endpoint not found
        429: Rate limit exceeded
    """
```

**Changes from Current Implementation**:
1. Add sandbox existence check
2. Route to SandboxService if sandbox exists
3. Add "mode" field to response
4. Maintain existing proxy logic as fallback

### 5. Sandbox Views

**Location**: `sandbox/views.py`

**Purpose**: Provides API endpoints for sandbox management

**Interface**:

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_sandbox(request, project_id):
    """
    Generates sandbox environment for a project.
    
    Authorization:
    - User must be authenticated
    - User must own the project
    
    Args:
        project_id: ID of project to generate sandbox for
        
    Response:
        {
            "message": "Sandbox generated successfully",
            "environment_id": int,
            "collections": [
                {
                    "name": str,
                    "record_count": int
                }
            ]
        }
        
    Status Codes:
        200: Sandbox generated successfully
        403: User does not own project
        404: Project not found
    """
```

### 6. Custom Rate Throttle

**Location**: `execution/throttles.py` (new file)

**Purpose**: Implements IP-based rate limiting for execution endpoint

**Interface**:

```python
from rest_framework.throttling import AnonRateThrottle

class ExecutionRateThrottle(AnonRateThrottle):
    """
    Custom throttle class for execution endpoint.
    Limits requests to 10 per minute per IP address.
    """
    rate = '10/min'
    
    def get_cache_key(self, request, view):
        """
        Returns cache key based on IP address and project ID.
        
        Args:
            request: Django request object
            view: View being accessed
            
        Returns:
            Cache key string for rate limiting
        """
```

### 7. Frontend ClerkProvider Integration

**Location**: `devshowcase_frontend/src/App.jsx`

**Purpose**: Wraps application with Clerk authentication context

**Interface**:

```jsx
import { ClerkProvider, useAuth } from '@clerk/clerk-react';

function App() {
  const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
  
  return (
    <ClerkProvider publishableKey={clerkPubKey}>
      <AuthenticatedApp />
    </ClerkProvider>
  );
}

function AuthenticatedApp() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  
  // Attach token to API requests
  // Provide auth state to components
}
```

### 8. API Client with Token Injection

**Location**: `devshowcase_frontend/src/utils/api.js`

**Purpose**: Centralized API client that injects Clerk JWT tokens

**Interface**:

```javascript
import { useAuth } from '@clerk/clerk-react';

export const createApiClient = (getToken) => {
  return {
    async request(url, options = {}) {
      const token = await getToken();
      
      const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(url, {
        ...options,
        headers,
      });
      
      return response.json();
    },
    
    get(url, options) {
      return this.request(url, { ...options, method: 'GET' });
    },
    
    post(url, data, options) {
      return this.request(url, {
        ...options,
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    
    // ... other methods
  };
};
```

## Data Models

### Database Schema

```sql
-- Existing Project table (reference)
CREATE TABLE projects_project (
    id INTEGER PRIMARY KEY,
    owner_id INTEGER REFERENCES auth_user(id),
    title VARCHAR(255),
    slug VARCHAR(255) UNIQUE,
    short_description TEXT,
    problem_statement TEXT,
    category VARCHAR(100),
    github_url VARCHAR(200),
    demo_url VARCHAR(200),
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);

-- Existing Endpoint table (reference)
CREATE TABLE projects_endpoint (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects_project(id),
    name VARCHAR(255),
    method VARCHAR(10),
    url VARCHAR(200),
    headers JSON,
    sample_body JSON,
    description TEXT,
    sample_response JSON
);

-- New Sandbox tables
CREATE TABLE sandbox_sandboxenvironment (
    id INTEGER PRIMARY KEY,
    project_id INTEGER UNIQUE REFERENCES projects_project(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sandbox_sandboxcollection (
    id INTEGER PRIMARY KEY,
    environment_id INTEGER REFERENCES sandbox_sandboxenvironment(id) ON DELETE CASCADE,
    name VARCHAR(100),
    UNIQUE(environment_id, name)
);

CREATE TABLE sandbox_sandboxrecord (
    id INTEGER PRIMARY KEY,
    collection_id INTEGER REFERENCES sandbox_sandboxcollection(id) ON DELETE CASCADE,
    data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_sandbox_collection_env ON sandbox_sandboxcollection(environment_id);
CREATE INDEX idx_sandbox_record_collection ON sandbox_sandboxrecord(collection_id);
```

### Data Flow Diagrams

#### Sandbox Generation Data Flow

```
Project with Endpoints
        │
        ├─ Endpoint 1: GET /api/users
        │  └─ sample_response: [{"id": 1, "name": "John"}, ...]
        │
        ├─ Endpoint 2: POST /api/expenses
        │  └─ sample_response: {"id": 1, "amount": 100}
        │
        └─ Endpoint 3: GET /api/expenses/1
           └─ sample_response: {"id": 1, "amount": 100}
           
                    ↓ Generate Sandbox
                    
SandboxEnvironment (project_id=1)
        │
        ├─ SandboxCollection (name="users")
        │  ├─ SandboxRecord (data={"id": 1, "name": "John"})
        │  └─ SandboxRecord (data={"id": 2, "name": "Jane"})
        │
        └─ SandboxCollection (name="expenses")
           └─ SandboxRecord (data={"id": 1, "amount": 100})
```

#### Request Execution Data Flow

```
Client Request
    │
    ├─ endpoint_id: 5
    ├─ custom_body: {"amount": 200}
    └─ Authorization: Bearer <jwt>
    
            ↓
            
Execution View
    │
    ├─ Authenticate user
    ├─ Check permissions
    ├─ Retrieve endpoint
    └─ Check sandbox exists
    
            ↓ (sandbox exists)
            
SandboxService
    │
    ├─ Extract resource: "expenses"
    ├─ Find collection: SandboxCollection(name="expenses")
    ├─ Execute POST operation
    ├─ Create new record with merged data
    └─ Return response
    
            ↓
            
Unified Response
    {
        "mode": "sandbox",
        "status_code": 201,
        "data": {"id": 2, "amount": 200},
        "error": null
    }
```

### Resource Name Extraction Algorithm

The system extracts REST resource names from endpoint URLs using the following algorithm:

```python
def extract_resource_name(url: str) -> str:
    """
    Extracts the primary resource name from a URL.
    
    Algorithm:
    1. Parse URL to get path component
    2. Split path by '/'
    3. Filter out empty strings, 'api', version strings (v1, v2, etc.)
    4. Find first segment that looks like a resource (plural noun)
    5. Remove numeric IDs from consideration
    6. Return the resource name
    
    Examples:
        "https://api.example.com/users" -> "users"
        "https://api.example.com/api/v1/expenses" -> "expenses"
        "https://api.example.com/users/123" -> "users"
        "https://api.example.com/api/v2/users/123/posts" -> "users"
    """
    from urllib.parse import urlparse
    
    path = urlparse(url).path
    segments = [s for s in path.split('/') if s]
    
    # Filter out common API prefixes
    filtered = [
        s for s in segments 
        if s not in ['api', 'v1', 'v2', 'v3'] 
        and not s.isdigit()
    ]
    
    # Return first valid resource name
    return filtered[0] if filtered else 'default'
```

### Sample Response Processing

When generating sandbox data from sample responses:

1. **Array Response**: Create one SandboxRecord per array item
   ```json
   sample_response: [
       {"id": 1, "name": "John"},
       {"id": 2, "name": "Jane"}
   ]
   ```
   Creates 2 SandboxRecords in the collection

2. **Object Response**: Create single SandboxRecord
   ```json
   sample_response: {"id": 1, "name": "John"}
   ```
   Creates 1 SandboxRecord in the collection

3. **Empty/Missing Response**: Skip record creation
   ```json
   sample_response: null
   ```
   Collection created but no records added

4. **Duplicate Detection**: Compare JSON data before creating
   - If identical data exists, skip creation
   - Comparison is deep equality on JSON structure


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property Reflection

After analyzing all acceptance criteria, the following redundancies were identified and resolved:

**Authentication Properties (1.1-1.10)**:
- Properties 1.3, 1.4, 1.5 can be combined into a single comprehensive JWT validation property
- Properties 1.8, 1.9, 1.10 are edge cases that will be handled by the validation property and unit tests
- Property 1.6 and 1.7 can be combined into a single user extraction and creation property

**Authorization Properties (5.1-5.6)**:
- Properties 5.1, 5.2, 5.3, 5.4 can be combined into a single property about write operation restrictions
- Property 5.5 and 5.6 can be combined into a single property about allowed operations

**Sandbox CRUD Properties (4.4-4.9)**:
- Each HTTP method has distinct behavior, so these remain separate properties
- Property 4.10 is subsumed by the individual method properties

**Cascade Deletion Properties (10.8, 10.9)**:
- These can be combined into a single cascade deletion property

**Dual Authentication Properties (12.1-12.3)**:
- These can be combined into a single property about authentication fallback

### Property 1: Bearer Token Extraction

For any HTTP request with an Authorization header in the format "Bearer <token>", the authentication handler should correctly extract the token portion after "Bearer ".

**Validates: Requirements 1.1**

### Property 2: JWT Validation

For any JWT token, when validated against the JWKS public keys, the authentication handler should accept the token if and only if: (1) the signature is valid using RS256 algorithm, (2) the audience matches the configured Clerk frontend API identifier, and (3) the token has not expired.

**Validates: Requirements 1.3, 1.4, 1.5**

### Property 3: User Creation from JWT

For any valid JWT token with a "sub" claim, the authentication handler should either retrieve an existing Django User with username matching the sub claim, or create a new User if none exists, ensuring the same token always resolves to the same user.

**Validates: Requirements 1.6, 1.7**

### Property 4: API Request Token Injection

For any API request made through the authenticated API client, if a valid JWT token is available from Clerk, the request should include an Authorization header with the token in Bearer format.

**Validates: Requirements 2.4**

### Property 5: Sandbox Environment Creation

For any project owned by an authenticated user, when sandbox generation is requested, a SandboxEnvironment should be created or retrieved (if already exists) with a one-to-one relationship to the project.

**Validates: Requirements 3.1, 3.6**

### Property 6: Resource Name Extraction

For any endpoint URL, the sandbox service should extract a resource name by parsing the URL path, filtering out common API prefixes (api, v1, v2, etc.) and numeric IDs, and returning the first valid resource segment.

**Validates: Requirements 3.2**

### Property 7: Collection Creation from Resources

For any extracted resource name during sandbox generation, a SandboxCollection should be created with that name, ensuring uniqueness within the environment (no duplicate collections for the same resource).

**Validates: Requirements 3.3**

### Property 8: Array Response Processing

For any endpoint with a sample_response that is a JSON array, the sandbox service should create one SandboxRecord per array item in the corresponding collection, with each record containing the data from one array element.

**Validates: Requirements 3.4**

### Property 9: Object Response Processing

For any endpoint with a sample_response that is a JSON object, the sandbox service should create exactly one SandboxRecord in the corresponding collection with the object data.

**Validates: Requirements 3.5**

### Property 10: Duplicate Record Prevention

For any sandbox collection, when adding records during generation, if a record with identical JSON data already exists in the collection, no duplicate record should be created.

**Validates: Requirements 3.7**

### Property 11: Sandbox Routing Decision

For any endpoint execution request, the execution view should check if a SandboxEnvironment exists for the endpoint's project, and route to sandbox service if it exists, otherwise route to proxy service.

**Validates: Requirements 4.1, 4.2, 4.3**

### Property 12: Sandbox GET All Records

For any GET request in sandbox mode without an ID in the URL, the sandbox service should return all SandboxRecords from the corresponding collection as a JSON array with status code 200.

**Validates: Requirements 4.4**

### Property 13: Sandbox GET Single Record

For any GET request in sandbox mode with a numeric ID in the URL, the sandbox service should return the specific SandboxRecord matching that ID with status code 200, or return status code 404 if no matching record exists.

**Validates: Requirements 4.5**

### Property 14: Sandbox POST Record Creation

For any POST request in sandbox mode with a request body, the sandbox service should create a new SandboxRecord with a generated ID merged with the request body data, add it to the collection, and return the created record with status code 201.

**Validates: Requirements 4.6**

### Property 15: Sandbox PUT Record Replacement

For any PUT request in sandbox mode with a numeric ID in the URL and a request body, the sandbox service should replace the existing record's data with the request body (merged with the ID), and return the updated record with status code 200, or return status code 404 if the record doesn't exist.

**Validates: Requirements 4.7**

### Property 16: Sandbox PATCH Record Merging

For any PATCH request in sandbox mode with a numeric ID in the URL and a request body, the sandbox service should merge the request body with the existing record's data (preserving fields not in the request), and return the updated record with status code 200, or return status code 404 if the record doesn't exist.

**Validates: Requirements 4.8**

### Property 17: Sandbox DELETE Record Removal

For any DELETE request in sandbox mode with a numeric ID in the URL, the sandbox service should remove the record from the collection and return status code 204, or return status code 404 if the record doesn't exist.

**Validates: Requirements 4.9**

### Property 18: Sandbox Isolation

For any request executed in sandbox mode, the sandbox service should never make HTTP requests to external APIs, ensuring complete isolation from external systems.

**Validates: Requirements 4.11, 7.2**

### Property 19: Write Operation Authorization

For any unauthenticated user attempting to execute a POST, PUT, PATCH, or DELETE request, the execution view should return a 403 forbidden error, while GET requests should be processed normally.

**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

### Property 20: Authenticated User Access

For any authenticated user, the execution view should process all HTTP method requests (GET, POST, PUT, PATCH, DELETE) normally without authorization errors.

**Validates: Requirements 5.6**

### Property 21: Rate Limit Independence

For any two different IP addresses making requests to the execution endpoint, the rate limit counters should be tracked independently, such that one IP reaching its limit does not affect the other IP's ability to make requests.

**Validates: Requirements 6.3**

### Property 22: Rate Limit Application

For any request to the execution endpoint (whether sandbox or proxy mode), the rate limiter should apply the 10 requests per minute limit, ensuring consistent rate limiting across both execution modes.

**Validates: Requirements 6.5**

### Property 23: Cascade Deletion

For any SandboxEnvironment that is deleted, all associated SandboxCollections and their SandboxRecords should be automatically deleted from the database, and similarly, deleting a SandboxCollection should delete all its SandboxRecords.

**Validates: Requirements 7.3, 10.8, 10.9**

### Property 24: Sandbox Data Isolation

For any two different projects with sandbox environments, accessing sandbox data for one project should only return records from that project's SandboxEnvironment, never returning records from another project's sandbox.

**Validates: Requirements 7.4, 7.5**

### Property 25: Collection Name Uniqueness

For any SandboxEnvironment, attempting to create two SandboxCollections with the same name should result in a database constraint violation, ensuring each collection name is unique within an environment.

**Validates: Requirements 10.4**

### Property 26: Auto-Timestamp Creation

For any newly created SandboxEnvironment, the created_at field should be automatically set to the current timestamp without manual intervention.

**Validates: Requirements 10.6**

### Property 27: Auto-Timestamp Update

For any SandboxRecord that is modified, the updated_at field should be automatically updated to the current timestamp, and the new timestamp should be greater than the previous timestamp.

**Validates: Requirements 10.7**

### Property 28: Response Format Consistency

For any request to sandbox endpoints, the response should be valid JSON with an appropriate HTTP status code (200, 201, 204, 400, 403, 404, 429).

**Validates: Requirements 11.5**

### Property 29: Dual Authentication Support

For any HTTP request, the backend should attempt authentication using ClerkAuthentication first, and if that returns None (no Bearer token), fall back to TokenAuthentication, allowing both authentication methods to work simultaneously.

**Validates: Requirements 12.1, 12.2, 12.3**

## Error Handling

### Authentication Errors

**Invalid JWT Signature**:
- Error Type: `AuthenticationFailed`
- HTTP Status: 401 Unauthorized
- Message: "Invalid token"
- Cause: JWT signature verification fails against JWKS public keys
- Recovery: User must re-authenticate with Clerk to obtain a new valid token

**Expired JWT Token**:
- Error Type: `AuthenticationFailed`
- HTTP Status: 401 Unauthorized
- Message: "Token expired"
- Cause: JWT exp claim is in the past
- Recovery: Frontend should automatically refresh token using Clerk's token refresh mechanism

**Audience Mismatch**:
- Error Type: `AuthenticationFailed`
- HTTP Status: 401 Unauthorized
- Message: "Invalid token"
- Cause: JWT aud claim doesn't match configured CLERK_AUDIENCE
- Recovery: Configuration error - verify CLERK_AUDIENCE environment variable matches Clerk dashboard settings

**JWKS Fetch Failure**:
- Error Type: `AuthenticationFailed`
- HTTP Status: 401 Unauthorized
- Message: "Authentication failed: [error details]"
- Cause: Network error or invalid CLERK_DOMAIN when fetching JWKS
- Recovery: Check network connectivity and CLERK_DOMAIN configuration

### Sandbox Errors

**Collection Not Found**:
- Error Type: `ValueError`
- HTTP Status: 404 Not Found
- Response: `{"mode": "sandbox", "status_code": 404, "data": null, "error": "Collection not found"}`
- Cause: Requested resource doesn't exist in sandbox environment
- Recovery: Generate sandbox or verify endpoint URL matches available collections

**Record Not Found**:
- Error Type: None (handled gracefully)
- HTTP Status: 200 (wrapper) with inner 404
- Response: `{"mode": "sandbox", "status_code": 404, "data": null, "error": "Record not found"}`
- Cause: Requested record ID doesn't exist in collection
- Recovery: Verify record ID or create record using POST

**Invalid Resource Extraction**:
- Error Type: None (uses default)
- HTTP Status: 200 (continues with "default" collection)
- Cause: URL path doesn't contain valid resource name
- Recovery: Ensure endpoint URLs follow REST conventions with resource names

**Duplicate Collection**:
- Error Type: `IntegrityError`
- HTTP Status: 500 Internal Server Error
- Cause: Attempting to create collection with duplicate name in same environment
- Recovery: Internal error - should be prevented by generation logic

### Authorization Errors

**Unauthorized Write Operation**:
- Error Type: None
- HTTP Status: 403 Forbidden
- Response: `{"error": "Only GET requests allowed for public users"}`
- Cause: Unauthenticated user attempting POST, PUT, PATCH, or DELETE
- Recovery: User must authenticate with Clerk to perform write operations

**Project Not Owned**:
- Error Type: None
- HTTP Status: 404 Not Found (security through obscurity)
- Response: `{"error": "Project not found"}`
- Cause: User attempting to generate sandbox for project they don't own
- Recovery: User can only generate sandboxes for their own projects

**Unpublished Project**:
- Error Type: None
- HTTP Status: 403 Forbidden
- Response: `{"error": "Project is not published"}`
- Cause: Attempting to execute endpoint for unpublished project
- Recovery: Project owner must publish project before endpoints can be executed

### Rate Limiting Errors

**Rate Limit Exceeded**:
- Error Type: `Ratelimited` (django-ratelimit)
- HTTP Status: 429 Too Many Requests
- Response: `{"error": "Rate limit exceeded"}`
- Cause: IP address exceeded 10 requests per minute
- Recovery: Wait until rate limit window resets (up to 60 seconds)

### Proxy Errors

**Request Timeout**:
- Error Type: `requests.exceptions.Timeout`
- HTTP Status: 200 (wrapper) with inner 408
- Response: `{"mode": "proxy", "status_code": 408, "data": null, "error": "Request timeout"}`
- Cause: External API didn't respond within 10 seconds
- Recovery: Retry request or check external API availability

**Request Exception**:
- Error Type: `requests.exceptions.RequestException`
- HTTP Status: 200 (wrapper) with inner 500
- Response: `{"mode": "proxy", "status_code": 500, "data": null, "error": "[exception details]"}`
- Cause: Network error, DNS failure, or other request-level error
- Recovery: Check endpoint URL and network connectivity

### Configuration Errors

**Missing Clerk Configuration**:
- Error Type: None (uses defaults)
- HTTP Status: N/A
- Cause: CLERK_DOMAIN or CLERK_AUDIENCE not set in environment
- Recovery: Set environment variables or accept default placeholder values for development

**Missing Clerk Publishable Key (Frontend)**:
- Error Type: None
- HTTP Status: N/A
- Display: Configuration error message in UI
- Cause: VITE_CLERK_PUBLISHABLE_KEY not set in frontend environment
- Recovery: Set environment variable in .env file

### Error Handling Strategy

**Graceful Degradation**:
- Authentication failures don't crash the application
- Missing sandbox collections return 404 instead of 500
- Configuration errors use sensible defaults where possible

**Unified Response Format**:
- All execution responses use consistent structure: `{mode, status_code, data, error}`
- Always return HTTP 200 from execution endpoint with actual status in response body
- Simplifies frontend error handling

**Security Considerations**:
- Don't expose internal error details to unauthenticated users
- Use 404 instead of 403 for ownership checks (security through obscurity)
- Log detailed errors server-side for debugging

**User-Friendly Messages**:
- Authentication errors guide users to re-authenticate
- Rate limit errors indicate wait time
- Sandbox errors suggest corrective actions

## Testing Strategy

### Dual Testing Approach

This feature requires both unit testing and property-based testing to ensure comprehensive coverage:

**Unit Tests**: Focus on specific examples, edge cases, and integration points
- Specific JWT token validation scenarios
- Frontend component rendering and user interactions
- Database model relationships and constraints
- API endpoint routing and response formats
- Configuration loading and default values
- Error message formatting

**Property-Based Tests**: Focus on universal properties across all inputs
- JWT validation with randomly generated tokens
- Sandbox CRUD operations with random data
- Resource name extraction from random URLs
- Authentication and authorization across random user states
- Rate limiting with random request patterns
- Data isolation across random project combinations

### Property-Based Testing Configuration

**Library Selection**:
- **Backend (Python)**: Use `hypothesis` library for property-based testing
- **Frontend (JavaScript)**: Use `fast-check` library for property-based testing

**Test Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each property test must reference its design document property
- Tag format: `# Feature: clerk-auth-sandbox-integration, Property {number}: {property_text}`

**Example Property Test Structure** (Python):

```python
from hypothesis import given, strategies as st
import pytest

# Feature: clerk-auth-sandbox-integration, Property 6: Resource Name Extraction
@given(
    protocol=st.sampled_from(['http', 'https']),
    domain=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('L', 'N'))),
    resource=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('L',))),
    has_id=st.booleans(),
    resource_id=st.integers(min_value=1, max_value=10000)
)
@pytest.mark.property_test
def test_resource_extraction_property(protocol, domain, resource, has_id, resource_id):
    """
    Property: For any endpoint URL, resource name extraction should return
    the resource segment regardless of protocol, domain, or ID presence.
    """
    if has_id:
        url = f"{protocol}://{domain}/api/v1/{resource}/{resource_id}"
    else:
        url = f"{protocol}://{domain}/api/v1/{resource}"
    
    extracted = SandboxService.extract_resource_name(url)
    assert extracted == resource
```

### Backend Testing Strategy

**Authentication Tests**:

Unit Tests:
- Test JWKS fetching with mocked Clerk endpoint
- Test JWT validation with specific valid/invalid tokens
- Test user creation vs. retrieval scenarios
- Test authentication fallback order (Clerk → Token)
- Test error messages for expired/invalid tokens

Property Tests:
- Property 1: Bearer token extraction with random header formats
- Property 2: JWT validation with randomly generated valid/invalid tokens
- Property 3: User creation consistency with random user IDs
- Property 29: Dual authentication with random auth header combinations

**Sandbox Generation Tests**:

Unit Tests:
- Test generation with empty project (no endpoints)
- Test generation with single endpoint
- Test generation with array vs. object sample responses
- Test generation idempotence (calling twice)
- Test ownership verification

Property Tests:
- Property 5: Sandbox creation with random projects
- Property 6: Resource extraction with random URLs
- Property 7: Collection creation with random resource names
- Property 8: Array processing with random array sizes
- Property 9: Object processing with random object structures
- Property 10: Duplicate prevention with random data

**Sandbox Execution Tests**:

Unit Tests:
- Test each HTTP method (GET, POST, PUT, PATCH, DELETE) with specific data
- Test 404 responses for missing collections/records
- Test response format structure
- Test ID extraction from URLs

Property Tests:
- Property 11: Routing decision with random sandbox states
- Property 12: GET all with random collection sizes
- Property 13: GET by ID with random IDs
- Property 14: POST with random request bodies
- Property 15: PUT with random updates
- Property 16: PATCH with random partial updates
- Property 17: DELETE with random records
- Property 18: Isolation verification (no external calls)

**Authorization Tests**:

Unit Tests:
- Test each HTTP method with authenticated user
- Test each HTTP method with unauthenticated user
- Test GET specifically for public access

Property Tests:
- Property 19: Write restrictions with random methods and auth states
- Property 20: Authenticated access with random methods

**Rate Limiting Tests**:

Unit Tests:
- Test exactly 10 requests succeed
- Test 11th request fails with 429
- Test reset after 60 seconds
- Test different IPs independently

Property Tests:
- Property 21: IP independence with random IP addresses
- Property 22: Rate limit application across modes

**Data Model Tests**:

Unit Tests:
- Test one-to-one relationship (Project ↔ SandboxEnvironment)
- Test foreign key relationships
- Test cascade deletion
- Test unique constraint on collection names
- Test JSON field storage
- Test auto-timestamps

Property Tests:
- Property 23: Cascade deletion with random data hierarchies
- Property 24: Data isolation with random projects
- Property 25: Uniqueness constraint with random collection names
- Property 26: Auto-timestamp creation
- Property 27: Auto-timestamp updates

### Frontend Testing Strategy

**Authentication Tests**:

Unit Tests:
- Test ClerkProvider wrapping
- Test publishable key configuration
- Test token retrieval after sign-in
- Test sign-out cleanup
- Test loading state display
- Test auth state propagation to children

Property Tests:
- Property 4: Token injection with random API requests

**Sandbox UI Tests**:

Unit Tests:
- Test sandbox button visibility for owners
- Test sandbox button hidden for non-owners
- Test button click triggers API call
- Test success message display
- Test error message display
- Test sandbox active indicator

**Integration Tests**:

Unit Tests:
- Test end-to-end flow: sign in → create project → generate sandbox → execute endpoint
- Test sandbox mode indicator in API playground
- Test proxy mode fallback when no sandbox
- Test error handling across the stack

### Test Data Generators

**Hypothesis Strategies** (Python):

```python
from hypothesis import strategies as st

# Generate valid JWT-like structures
jwt_claims = st.fixed_dictionaries({
    'sub': st.text(min_size=10, max_size=50),
    'aud': st.text(min_size=10, max_size=50),
    'exp': st.integers(min_value=0, max_value=2147483647),
    'iat': st.integers(min_value=0, max_value=2147483647),
})

# Generate endpoint URLs
endpoint_urls = st.builds(
    lambda protocol, domain, resource, has_id, id_val: 
        f"{protocol}://{domain}/api/v1/{resource}" + (f"/{id_val}" if has_id else ""),
    protocol=st.sampled_from(['http', 'https']),
    domain=st.text(min_size=5, max_size=20),
    resource=st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('L',))),
    has_id=st.booleans(),
    id_val=st.integers(min_value=1, max_value=10000)
)

# Generate JSON data for sandbox records
json_data = st.recursive(
    st.one_of(
        st.none(),
        st.booleans(),
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.text(),
    ),
    lambda children: st.one_of(
        st.lists(children, max_size=10),
        st.dictionaries(st.text(min_size=1, max_size=20), children, max_size=10)
    ),
    max_leaves=20
)

# Generate HTTP methods
http_methods = st.sampled_from(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])

# Generate IP addresses
ip_addresses = st.builds(
    lambda a, b, c, d: f"{a}.{b}.{c}.{d}",
    a=st.integers(min_value=1, max_value=255),
    b=st.integers(min_value=0, max_value=255),
    c=st.integers(min_value=0, max_value=255),
    d=st.integers(min_value=1, max_value=255)
)
```

**Fast-Check Arbitraries** (JavaScript):

```javascript
import fc from 'fast-check';

// Generate API request configurations
const apiRequestArb = fc.record({
  url: fc.webUrl(),
  method: fc.constantFrom('GET', 'POST', 'PUT', 'PATCH', 'DELETE'),
  body: fc.option(fc.jsonValue(), { nil: null }),
  headers: fc.dictionary(fc.string(), fc.string())
});

// Generate sandbox data
const sandboxRecordArb = fc.jsonValue();

// Generate resource names
const resourceNameArb = fc.stringOf(
  fc.constantFrom(...'abcdefghijklmnopqrstuvwxyz'),
  { minLength: 3, maxLength: 20 }
);
```

### Test Coverage Goals

**Backend**:
- Line coverage: >90%
- Branch coverage: >85%
- Property test iterations: 100 per property
- Unit test count: ~80-100 tests

**Frontend**:
- Component coverage: >85%
- Integration test coverage: >75%
- Property test iterations: 100 per property
- Unit test count: ~40-50 tests

### Continuous Integration

**Test Execution**:
- Run all unit tests on every commit
- Run property tests on every pull request
- Run integration tests before deployment
- Fail build if any test fails or coverage drops

**Performance Monitoring**:
- Property tests should complete within 30 seconds per test file
- Unit tests should complete within 5 seconds per test file
- Flag slow tests for optimization

**Test Reporting**:
- Generate coverage reports for each test run
- Track property test failure rates
- Log counterexamples from failed property tests for debugging
