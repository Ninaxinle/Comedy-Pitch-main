# Comedy Peach - Full-Stack Comedy Platform Backend

A comprehensive Python FastAPI backend for the Comedy Peach platform, featuring Firebase Authentication, video/audio uploads, AI analytics, user management, and a complete testing framework.

## 🚀 Features

### 🔐 Authentication & Security
- **Firebase Authentication** with email/password and Google sign-in
- **JWT Token Verification** for protected API endpoints
- **User Management** with profile operations and admin functions
- **Password Reset** functionality
- **CORS Protection** and security middleware

### 📹 Video & Media Management
- **Video/Audio Upload** with multiple storage backends (S3, MinIO)
- **File Processing** with format validation and metadata extraction
- **Streaming Support** for efficient media delivery
- **Transcript Management** for accessibility
- **Playback Analytics** tracking

### 👥 User & Social Features
- **User Profiles** with customizable information
- **Like System** for video interactions
- **Feed Generation** with pagination and filtering
- **User Search** and discovery features
- **Admin Panel** for user management

### 🤖 AI & Analytics
- **ML Processing** integration for content analysis
- **Analytics Data** collection and storage
- **Content Insights** and recommendations
- **Performance Metrics** tracking

### 🧪 Testing & Quality
- **Comprehensive Test Suite** with 128+ tests
- **Pytest Framework** with async support
- **Mocked Dependencies** for reliable testing
- **Database Isolation** with test-specific databases
- **API Integration Tests** for all endpoints
- **Interactive Test UIs** for authentication and upload testing

## 📁 Project Structure

```
backend/
├── config/
│   ├── __init__.py
│   ├── firebase_config.py      # Firebase Admin SDK configuration
│   └── database.py             # Database configuration and initialization
├── models/
│   ├── __init__.py
│   ├── models.py               # SQLAlchemy model registry
│   ├── user.py                 # User model and operations
│   ├── video.py                # Video model and operations
│   ├── like.py                 # Like model and operations
│   └── analytics.py            # Analytics data model
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # Authentication API routes
│   ├── videos.py               # Video management API routes
│   ├── users.py                # User management API routes
│   ├── likes.py                # Like system API routes
│   └── ml.py                   # ML processing API routes
├── storage/
│   └── backends/               # Storage backend implementations
├── tests/
│   ├── conftest.py             # Pytest configuration and fixtures
│   ├── test_models.py          # Database model tests
│   ├── test_storage.py         # Storage backend tests
│   ├── test_auth_integration.py # Authentication integration tests
│   ├── test_video_apis.py      # Video API endpoint tests
│   ├── test_user_apis.py       # User API endpoint tests
│   ├── test_likes_apis.py      # Like system API tests
│   └── test_ml_apis.py         # ML processing API tests
├── test-auth-ui/
│   ├── index.html              # Authentication test interface
│   └── auth.js                 # Frontend authentication logic
├── test-upload-ui/
│   └── index.html              # Video upload test interface
├── uploads/                    # Local file storage (if using local backend)
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── env.example                 # Environment variables template
├── test_firebase_users.py      # Firebase connection test script
└── README.md                   # This file
```

## 🔧 Setup Instructions

### 1. Prerequisites

- **Python 3.8+** with virtual environment support
- **Firebase project** with Authentication enabled
- **Storage backend** (Local, AWS S3, or MinIO)
- **Database** (SQLite for development, PostgreSQL for production)

### 2. Firebase Project Setup

1. **Create a Firebase Project:**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create a new project or use existing one

2. **Enable Authentication:**
   - Go to Authentication → Sign-in method
   - Enable **Email/Password** provider
   - Enable **Google** provider (optional)

3. **Add Web App:**
   - Go to Project Settings → General
   - Click "Add app" → Web
   - Register your app and copy the configuration

4. **Get Service Account:**
   - Go to Project Settings → Service accounts
   - Click "Generate new private key"
   - Download the JSON file

5. **Configure Authorized Domains:**
   - Go to Authentication → Settings → Authorized domains
   - Add `localhost` for local development

### 3. Environment Configuration

1. **Copy environment template:**
   ```bash
   cp env.example .env
   ```

2. **Configure your environment variables in `.env`:**
   ```bash
   # Firebase Admin SDK (from service account JSON)
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com

   # Firebase Web Config (from web app config)
   FIREBASE_API_KEY=AIzaSyC...
   FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com
   FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
   FIREBASE_MESSAGING_SENDER_ID=123456789
   FIREBASE_APP_ID=1:123456789:web:abcdef123456

   # Database Configuration
   DATABASE_URL=sqlite:///./comedy_peach.db

   # Storage Configuration
   STORAGE_BACKEND=local  # Options: local, s3, minio
   
   # For S3 Storage (optional)
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=your-bucket-name

   # For MinIO Storage (optional)
   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=minioadmin
   MINIO_SECRET_KEY=minioadmin
   MINIO_BUCKET_NAME=comedy-peach
   MINIO_SECURE=false

   # Server Configuration
   PORT=8000
   ```

### 4. MinIO Setup (Mock S3 for Development)

For local development, you can use MinIO as a mock S3 service:

1. **Download MinIO Community Edition:**
   - Go to: https://github.com/minio/minio/releases
   - Download the latest `minio.exe` for Windows
   - Or use direct download: https://dl.min.io/server/minio/release/windows-amd64/minio.exe

2. **Start MinIO Server:**
   ```bash
   # Create data directory
   mkdir C:\minio-data
   
   # Start MinIO server
   minio.exe server C:\minio-data --console-address :9001
   ```

3. **Access MinIO Console:**
   - **MinIO API:** http://localhost:9000
   - **MinIO Console:** http://localhost:9001
   - **Login:** minioadmin / minioadmin

4. **Configure for MinIO:**
   ```bash
   # Update your .env file
   STORAGE_BACKEND=minio
   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=minioadmin
   MINIO_SECRET_KEY=minioadmin
   MINIO_BUCKET_NAME=comedy-peach
   MINIO_SECURE=false
   ```

5. **Test MinIO Setup:**
   ```bash
   python test_minio_setup.py
   ```

### 4. Installation & Setup

1. **Create and activate virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize database:**
   ```bash
   # The database will be automatically initialized when you start the server
   # For manual initialization, you can run the database setup in Python
   ```

4. **Start the server:**
   ```bash
   python main.py
   ```

5. **Access the application:**
   - **API Documentation:** http://localhost:8000/docs
   - **Test Auth UI:** http://localhost:8000/test-auth-ui
   - **Test Upload UI:** http://localhost:8000/test-upload-ui
   - **Health Check:** http://localhost:8000/

## 🌐 API Endpoints

### Authentication (`/api/auth`)
- `POST /verify-token` - Verify Firebase ID token
- `GET /profile` - Get current user profile (protected)
- `GET /users` - List all users (admin only)
- `POST /custom-token` - Create custom token (testing)
- `GET /health` - Authentication service health check
- `GET /config` - Firebase web configuration

### Videos (`/api/videos`)
- `POST /uploads/presign` - Get presigned upload URL
- `POST /` - Submit video metadata after upload
- `GET /` - Get video feed with pagination
- `GET /{video_id}` - Get specific video details
- `PUT /{video_id}` - Update video metadata
- `DELETE /{video_id}` - Delete video (owner only)
- `GET /{video_id}/analytics` - Get video analytics and transcript

### Users (`/api/users`)
- `GET /profile` - Get current user profile
- `PUT /profile` - Update user profile
- `GET /{user_id}` - Get user profile by ID
- `GET /search` - Search users
- `DELETE /{user_id}` - Delete user (admin only)

### Likes (`/api/videos/{video_id}/likes`)
- `POST /` - Like a video
- `DELETE /` - Unlike a video
- `GET /` - Get like count and user like status

### ML Processing (`/api/ml`)
- `POST /analyze/{video_id}` - Analyze video content
- `GET /analytics/{video_id}` - Get video analytics
- `POST /transcribe/{video_id}` - Generate transcript
- `GET /recommendations` - Get content recommendations

## 🧪 Testing

### Test UIs

The project includes two test interfaces for easy development and testing:

#### 1. Authentication Test UI (`/test-auth-ui`)
- **Purpose:** Test Firebase authentication
- **URL:** http://localhost:8000/test-auth-ui
- **Features:**
  - Firebase sign-in with email/password or Google
  - Display Firebase ID token for API testing
  - Test protected endpoints

#### 2. Video Upload Test UI (`/test-upload-ui`)
- **Purpose:** Test complete video upload flow
- **URL:** http://localhost:8000/test-upload-ui
- **Features:**
  - Step-by-step upload process
  - File selection with metadata auto-fill
  - Presigned URL generation
  - Direct upload to MinIO/S3
  - Video registration in database
  - Real-time status updates and error handling

### Upload Flow Testing

The upload system follows this flow:

1. **Get Presigned URL:** `POST /api/videos/uploads/presign`
   - Requires Firebase authentication
   - Returns upload URL and storage key

2. **Upload File:** Direct upload to storage (MinIO/S3)
   - Use the presigned URL with HTTP PUT
   - File uploads directly to storage backend

3. **Register Video:** `POST /api/videos/`
   - Submit metadata after successful upload
   - Creates video record in database

### Running Tests

1. **Run all tests:**
   ```bash
   pytest
   ```

2. **Run specific test categories:**
   ```bash
   # Model tests
   pytest tests/test_models.py
   
   # Storage tests
   pytest tests/test_storage.py
   
   # API tests
   pytest tests/test_video_apis.py
   pytest tests/test_user_apis.py
   pytest tests/test_likes_apis.py
   pytest tests/test_ml_apis.py
   
   # Authentication tests
   pytest tests/test_auth_integration.py
   ```

3. **Run with coverage:**
   ```bash
   pytest --cov=. --cov-report=html
   ```

4. **Run with verbose output:**
   ```bash
   pytest -v
   ```

### Test Features

- **128+ Comprehensive Tests** covering all major functionality
- **Database Isolation** with test-specific databases
- **Mocked Dependencies** for reliable testing
- **Async Test Support** for FastAPI endpoints
- **Storage Backend Testing** for all storage options
- **Authentication Integration** testing with Firebase mocks

## 🎨 User Interface

### Test Authentication Interface
Access the built-in test interface at `http://localhost:8000/test-auth-ui` to:

- **Sign In** with existing accounts
- **Create New Accounts** with email/password
- **Google Sign-in** integration
- **Test API Endpoints** with real authentication
- **Password Reset** functionality
- **User Profile Management**

### Features
- **Clean, Modern Design** with intuitive navigation
- **Real-time Feedback** with inline results
- **Color-coded Responses** (green for success, red for errors)
- **Comprehensive Testing** of all authentication flows

## 🛡️ Security Features

- **Firebase Authentication** with secure token verification
- **JWT Token Validation** for all protected endpoints
- **CORS Protection** with configurable origins
- **Input Validation** using Pydantic models
- **File Upload Security** with type and size validation
- **Database Security** with SQL injection protection
- **Error Handling** without information leakage

## 🚀 Deployment

### Development
```bash
# Start with auto-reload
python main.py
```

### Production
```bash
# Using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000

# Using gunicorn (recommended for production)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables for Production
- Set `STORAGE_BACKEND=s3` or `STORAGE_BACKEND=minio`
- Configure production database URL
- Set proper CORS origins
- Configure Firebase production settings

## 🚨 Troubleshooting

### Common Issues

1. **Firebase Connection Errors:**
   - Verify service account credentials
   - Check project ID and configuration
   - Ensure authorized domains include your domain

2. **Database Issues:**
   - Check database URL configuration
   - Ensure write permissions for SQLite files
   - Verify PostgreSQL connection (if using)

3. **File Upload Problems:**
   - Check storage backend configuration (MinIO/S3)
   - Verify file size limits
   - Ensure storage bucket permissions
   - Use the test upload UI for debugging: http://localhost:8000/test-upload-ui

4. **Authentication Failures:**
   - Verify Firebase configuration
   - Check token expiration
   - Ensure CORS settings are correct

5. **Test Failures:**
   - Run tests in isolation: `pytest tests/test_models.py -v`
   - Check database isolation
   - Verify mock configurations

### Debug Information
- **Server Logs:** Detailed logging in console output
- **API Documentation:** Available at `/docs` and `/redoc`
- **Health Check:** System status at `/`
- **Browser Console:** Frontend debugging information

## 📊 Performance & Monitoring

### Built-in Monitoring
- **Health Check Endpoint** with system status
- **Request Logging** for API calls
- **Error Tracking** with detailed stack traces
- **Performance Metrics** for uploads and processing

### Optimization Tips
- Use production storage backends (S3/MinIO) for better performance
- Configure proper database indexes
- Implement caching for frequently accessed data
- Use CDN for static file delivery

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Write tests** for new functionality
4. **Run the test suite** to ensure everything works
5. **Submit a pull request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for API changes
- Use type hints for better code quality

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section above
- Review the API documentation at `/docs`
- Run the test suite to verify your setup
- Check server logs for detailed error information

---

**🍑 Comedy Peach Backend** - Building the future of comedy content creation and sharing! 