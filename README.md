# 🧗 Climbing Tracker App

A modern climbing tracker web application built with FastAPI and MongoDB.

## Features

- 📊 Track climbing routes and progress
- 🎯 Record attempts and completion status
- 🎨 Modern, responsive web interface
- 🔒 Secure MongoDB integration
- 🚀 FastAPI backend with automatic API documentation

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: MongoDB Atlas
- **Frontend**: HTML5, CSS3, JavaScript
- **Templating**: Jinja2
- **Authentication**: OAuth (Google & Apple) - Coming Soon

## Project Structure

```
├── config/          # Database configuration
├── models/          # Pydantic data models
├── router/          # API route handlers
├── schema/          # Data serialization schemas
├── static/          # CSS, JS, and static assets
├── templates/       # HTML templates
├── main.py          # FastAPI application entry point
├── .env            # Environment variables (not tracked in git)
└── requirements.txt # Python dependencies
```

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Climbing_app
```

### 2. Create Virtual Environment
```bash
python -m venv env
# Windows
.\\env\\Scripts\\activate
# Linux/Mac
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install fastapi uvicorn pymongo python-dotenv jinja2
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
MONGODB_URL=your-mongodb-connection-string
DATABASE_NAME=ClimbingApp
COLLECTION_NAME=climbing_app_collection
SECRET_KEY=your-secret-key
```

### 5. Run the Application
```bash
uvicorn main:app --reload --port 8000
```

Visit `http://127.0.0.1:8000` to access the application.

## API Documentation

FastAPI provides automatic API documentation:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## API Endpoints

- `GET /` - Homepage
- `GET /trackers/` - Get all climbing trackers
- `POST /trackers/` - Add new climbing tracker
- `GET /health` - Health check endpoint

## Development

### Running in Development Mode
```bash
uvicorn main:app --reload --port 8000
```

### Project Dependencies
- fastapi
- uvicorn
- pymongo
- python-dotenv
- jinja2

## Security

- Environment variables are used for sensitive configuration
- MongoDB credentials are never committed to version control
- Comprehensive `.gitignore` prevents accidental exposure of secrets

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Future Features

- 🔐 OAuth authentication (Google & Apple)
- 📱 Mobile-responsive design improvements
- 📈 Advanced analytics and progress tracking
- 🗺️ Route location mapping
- 👥 Social features and route sharing

---

Made with ❤️ for the climbing community