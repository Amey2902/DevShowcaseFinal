# DevShowcase - Setup Instructions

## Backend Setup

### 1. Navigate to backend directory
```bash
cd devshowcase_backend
```

### 2. Create virtual environment
```bash
python -m venv venv
```

### 3. Activate virtual environment
Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run migrations
```bash
python manage.py makemigrations accounts
python manage.py makemigrations projects
python manage.py makemigrations execution
python manage.py migrate
```

### 6. Create superuser (optional)
```bash
python manage.py createsuperuser
```

### 7. Load seed data
```bash
python seed_data.py
```

### 8. Run development server
```bash
python manage.py runserver
```

Backend will run at: http://localhost:8000

## Frontend Setup

### 1. Navigate to frontend directory (in new terminal)
```bash
cd devshowcase_frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Run development server
```bash
npm run dev
```

Frontend will run at: http://localhost:3000

## Test Credentials

After running seed_data.py:
- Username: testuser
- Password: testpass123

## Production Configuration

### PostgreSQL Setup (for production)

1. Install PostgreSQL

2. Create database:
```sql
CREATE DATABASE devshowcase;
CREATE USER devshowcase_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE devshowcase TO devshowcase_user;
```

3. Update settings.py:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'devshowcase',
        'USER': 'devshowcase_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Environment Variables

Create .env file in backend:
```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Build Frontend for Production
```bash
cd devshowcase_frontend
npm run build
```

## API Endpoints

### Authentication
- POST /api/auth/register/
- POST /api/auth/login/
- POST /api/auth/logout/
- GET /api/auth/me/

### Projects (Public)
- GET /api/projects/
- GET /api/projects/{slug}/
- GET /api/projects/{slug}/full/

### Projects (Authenticated)
- POST /api/projects/create/
- PUT /api/projects/{slug}/update/
- DELETE /api/projects/{slug}/delete/
- POST /api/techstack/
- POST /api/architecture/
- POST /api/endpoints/
- POST /api/timeline/

### Execution
- POST /api/execute/

## Features

1. User authentication with token-based auth
2. Project creation with auto-generated slugs
3. Tab-based project editor:
   - Overview
   - Tech Stack
   - Architecture (draggable diagram)
   - API Endpoints
   - Timeline
   - Publish
4. Public project pages with API playground
5. Live API execution with security validation
6. Rate limiting on API execution
7. SSRF protection
8. Forbidden pattern detection

## Security Features

- Private IP blocking
- Forbidden URL pattern detection (admin, payment, localhost, etc.)
- Header validation (blocks api-key, secret, bearer sk_)
- Rate limiting (10 requests per minute per IP)
- Public users can only execute GET requests
- Request timeout (10 seconds)

## Notes

- Slug is auto-generated from project title
- Architecture node positions are saved on drag
- Only published projects are visible to public
- API responses are never stored in database
- All write operations require authentication
