# DevShowcase 🚀

An AI-powered developer portfolio platform that automatically analyzes code repositories and generates comprehensive project documentation, API documentation, and interactive showcases.

## ✨ Features

### 🤖 AI-Powered Analysis
- **Automatic endpoint detection** from uploaded code (Django, Flask, FastAPI, etc.)
- **Tech stack identification** and reasoning
- **Architecture diagram generation** 
- **Timeline creation** from git history
- **Code analysis** for frameworks, languages, and patterns

### 📋 Project Management
- **Multi-tab editor** (Overview, Tech Stack, Architecture, Endpoints, Timeline, Publish)
- **File/ZIP/GitHub upload** support
- **Real-time progress tracking** during analysis
- **Draft/Published states** for projects

### 🔌 API Documentation
- **Auto-detected endpoints** with metadata (method, URL, parameters, auth)
- **Manual endpoint creation** and editing
- **API playground** for testing endpoints
- **Code samples** generation
- **Parameter documentation** (path params, query params, headers)

### 🏗 Architecture Visualization
- **Interactive architecture diagrams**
- **Component relationships** mapping
- **Technology stack visualization**
- **Drag-and-drop** node positioning

## 🛠 Tech Stack

### Backend
- **Django REST Framework** - API endpoints
- **PostgreSQL** - Database
- **Celery** - Background tasks
- **Redis** - Caching and task queue
- **AI Integration** - Code analysis

### Frontend
- **React 18** - UI framework
- **Framer Motion** - Animations
- **Axios** - API calls
- **React Router** - Navigation
- **Modern CSS** - Styling

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL
- Redis

### Backend Setup
```bash
cd devshowcase_backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend Setup
```bash
cd devshowcase_frontend
npm install
npm start
```

### Background Tasks
```bash
# Start Celery worker
celery -A devshowcase_backend worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A devshowcase_backend beat --loglevel=info
```

## 📖 Usage

1. **Create Project** - Upload your code repository
2. **AI Analysis** - Let AI analyze your code structure
3. **Review & Edit** - Customize the generated documentation
4. **Publish** - Share your professional project showcase

## 🔧 Recent Updates

### ✅ Duplicate Endpoint Detection Fix
- Fixed endpoint accumulation bug during re-uploads
- Added pre-cleanup logic for auto-detected endpoints
- Preserved manual endpoints during re-uploads
- Comprehensive property-based testing

### ✅ Frontend Rendering Improvements
- Fixed React object rendering errors
- Enhanced parameter display for endpoints
- Improved error handling and loading states

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- AI-powered code analysis
- Modern web development practices
- Open source community

---

**Transform your code repositories into professional showcases with DevShowcase!** 🎯