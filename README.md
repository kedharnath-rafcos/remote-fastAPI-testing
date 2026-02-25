# EduSportsConnect FastAPI

A modern, async REST API built with FastAPI and PostgreSQL for managing educational sports programs.

## 🚀 Features

- ✅ **Async PostgreSQL Integration** - High-performance async database operations with SQLAlchemy 2.0+ and asyncpg
- ✅ **RESTful API** - Complete CRUD operations with proper HTTP methods and status codes
- ✅ **Auto-generated Documentation** - Interactive API docs with Swagger UI and ReDoc
- ✅ **Modular Architecture** - Domain-based folder structure for easy scalability
- ✅ **Type Safety** - Full type hints with Pydantic schemas for validation
- ✅ **CORS Support** - Configured for frontend integration
- ✅ **Database Connection Pooling** - Optimized async connection management
- ✅ **Environment-based Configuration** - Secure settings management with python-dotenv

## 📋 Prerequisites

- **Python 3.10 or higher** (tested with Python 3.14)
- **PostgreSQL 12 or higher** (tested with PostgreSQL 18.2)
- **Git** for version control
- Basic knowledge of FastAPI and async Python

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd EduSportsConnect-FastApi
```

### 2. Create Virtual Environment

**Important:** Virtual environments are NOT included in the repository. Each team member creates their own.

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Why not share venv?**
- Virtual environments are OS-specific and won't work across different systems
- They're large (100+ MB) and slow down repository operations
- Each developer may use different Python versions
- They can be recreated in seconds from `requirements.txt`

### 3. Install Dependencies

All required packages with exact versions are in `requirements.txt`:

```bash
pip install -r requirements.txt
```

This ensures everyone on your team has identical dependencies.

### 4. Configure Environment Variables

**Copy the example file and customize it:**

```bash
# Windows PowerShell
Copy-Item .env.example .env

# Linux/macOS
cp .env.example .env
```

**Edit `.env` file with your settings:**

```env
# Application Configuration
APP_NAME=EduSportsConnect API
APP_VERSION=1.0.0
DEBUG=True

# Database Configuration
# IMPORTANT: Use postgresql+asyncpg:// for async support (not postgresql://)
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/your_database_name
DATABASE_ECHO=True
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_PRE_PING=True

# CORS Settings (comma-separated list)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000

# Security Settings (Change in production!)
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**⚠️ Critical Notes:**
- **Replace** `your_password` and `your_database_name` with your actual PostgreSQL credentials
- **URL-encode special characters** in passwords:
  - `@` becomes `%40`
  - `#` becomes `%23`
  - `$` becomes `%24`
  - `&` becomes `%26`
  - Example: Password `Admin@123` → `Admin%40123`
- **Never commit `.env`** to version control (it's in `.gitignore`)
- **Each team member** has their own `.env` with their local database credentials
- **Use `.env.example`** as a template (this IS committed to git)

### 5. Setup PostgreSQL Database

**Option A: Using psql command line**

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE sports_db_test1;

# Grant permissions (if using different user)
GRANT ALL PRIVILEGES ON DATABASE sports_db_test1 TO your_username;

# Exit psql
\q
```

**Option B: Using pgAdmin**
1. Open pgAdmin
2. Right-click on "Databases" → Create → Database
3. Enter database name (e.g., `sports_db_test1`)
4. Click "Save"

**Note:** Database tables will be created automatically when you first run the application. The app uses SQLAlchemy's `create_all()` during startup.

### 6. Run the Application

```bash
# Development mode with auto-reload (recommended for development)
uvicorn app.main:app --reload

# Production mode (without auto-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Custom host and port
uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
```

**Successful startup output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Database connected successfully!
INFO:     Database tables initialized!
INFO:     Application startup complete.
```

**Access Points:**
- **API Root**: http://localhost:8000
- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Database Test**: http://localhost:8000/db-test

### 7. Verify Installation

Test the API is working:

```bash
# Using curl
curl http://localhost:8000/

# Or open in browser
start http://localhost:8000/docs  # Windows
open http://localhost:8000/docs   # macOS
```

## 📁 Project Structure

```
EduSportsConnect-FastApi/
├── app/
│   ├── __init__.py
│   ├── main.py                        # FastAPI application entry point
│   │
│   ├── core/                          # Core infrastructure
│   │   ├── __init__.py
│   │   ├── config.py                 # Configuration settings (Pydantic)
│   │   └── database.py               # Database connection & async session
│   │
│   ├── models/                        # SQLAlchemy database models
│   │   ├── __init__.py               # Exports all models
│   │   └── user.py                   # User model
│   │
│   ├── schemas/                       # Pydantic validation schemas
│   │   ├── __init__.py               # Exports all schemas  
│   │   └── user.py                   # User schemas
│   │
│   └── api/
│       └── endpoints/                 # API route handlers
│           ├── __init__.py
│           └── users.py              # User CRUD endpoints
│
├── .env                               # ❌ Environment variables (NOT in git)
├── .env.example                       # ✅ Environment template (in git)
├── .gitignore                         # ✅ Git ignore rules
├── requirements.txt                   # ✅ Python dependencies
├── README.md                          # ✅ This file
├── PROJECT_STRUCTURE.md               # ✅ Detailed architecture guide
└── PUSH_CHECKLIST.md                  # ✅ Pre-push verification guide

❌ NOT in repository (git ignores these):
├── venv/                              # Virtual environment
├── __pycache__/                       # Python cache
├── .env                               # Local credentials
└── *.pyc, *.pyo                       # Compiled Python files
```

**Key Points:**
- ✅ **DO commit**: Source code, requirements.txt, .env.example, documentation
- ❌ **DON'T commit**: venv/, .env, __pycache__/, IDE config, database files

## 🔌 API Endpoints

### Health Check
- `GET /` - Welcome message
- `GET /health` - Health check endpoint
- `GET /db-test` - Database connection test

### Users
- `GET /users/` - Get all users (with pagination)
- `GET /users/{user_id}` - Get user by ID
- `POST /users/` - Create new user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user
- `GET /users/email/{email}` - Get user by email

## 🧪 Testing the API

### Using Swagger UI
1. Navigate to http://localhost:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out" button
4. Fill in the required parameters
5. Click "Execute" to test

### Using cURL

```bash
# Create a user
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com"
  }'

# Get all users
curl "http://localhost:8000/users/"

# Get user by ID
curl "http://localhost:8000/users/1"
```

## 🔧 Development Guide

### Adding a New Entity (e.g., Sports)

Follow the modular pattern:

1. **Create Model**: `app/models/sport.py`
2. **Export Model**: Update `app/models/__init__.py`
3. **Create Schemas**: `app/schemas/sport.py`
4. **Export Schemas**: Update `app/schemas/__init__.py`
5. **Create Endpoints**: `app/api/endpoints/sports.py`
6. **Register Router**: Update `app/main.py`

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed examples.

### Code Style
- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Write docstrings for all functions and classes
- Keep functions focused and small

### Database Migrations
When you modify models, the tables will be auto-created on startup (development only). For production, consider using Alembic for migrations:

```bash
pip install alembic
alembic init alembic
# Configure alembic.ini and env.py
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 🐛 Troubleshooting

### Database Connection Issues

**Error:** `could not connect to server`
```bash
# Check if PostgreSQL is running
# Windows
Get-Service postgresql*

# Linux
sudo systemctl status postgresql

# macOS
brew services list
```

**Error:** `password authentication failed`
- Check credentials in `.env` file
- Ensure password is URL-encoded (e.g., `@` → `%40`)
- Verify user has access to the database

**Error:** `database "your_db" does not exist`
```sql
-- Create the database
CREATE DATABASE your_database_name;
```

**Error:** `asyncpg.exceptions.InvalidCatalogNameError`
- Database name in `.env` doesn't exist
- Create it using pgAdmin or psql

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'app'`
```bash
# Make sure you're in the project root directory
cd EduSportsConnect-FastApi

# Reinstall dependencies
pip install -r requirements.txt

# Clear Python cache
Get-ChildItem -Recurse -Filter __pycache__ | Remove-Item -Recurse -Force
```

**Error:** `ImportError: cannot import name 'async_sessionmaker'`
- You have an old version of SQLAlchemy
```bash
pip install --upgrade sqlalchemy
# Or reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use

**Error:** `ERROR: [Errno 48] Address already in use`

```bash
# Windows - Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### Virtual Environment Issues

**Issue:** venv activation not working

```bash
# Windows PowerShell (if execution policy blocks)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
.\venv\Scripts\activate

# Or use CMD instead
.\venv\Scripts\activate.bat
```

### Git Issues

**Issue:** `.env` file showing in git status

```bash
# Remove from git tracking (keeps local file)
git rm --cached .env

# Verify it's ignored
git check-ignore .env
# Should output: .env

# Add and commit the removal
git commit -m "Remove .env from version control"
```

### Database Migration Issues

**Issue:** Schema changes not reflecting

```bash
# Drop and recreate tables (CAUTION: loses data)
# In development only!
# Delete all tables manually via pgAdmin or:
DROP DATABASE your_database_name;
CREATE DATABASE your_database_name;

# Then restart the app to recreate tables
```

### Pydantic Validation Errors

**Error:** `validation error for Settings`
- Check `.env` file format
- Ensure no JSON arrays in .env (use comma-separated values)
- Check for typos in variable names
- Ensure all required variables are set

## 📚 Tech Stack

### Core Framework
- **FastAPI** 0.115.12 - Modern, fast web framework for building APIs
- **Uvicorn** 0.34.3 - Lightning-fast ASGI server

### Database
- **PostgreSQL** - Production-ready relational database
- **SQLAlchemy** 2.0+ - Async ORM for database operations
- **asyncpg** 0.29.0+ - High-performance async PostgreSQL driver
- **greenlet** 2.0.0+ - Async support for SQLAlchemy

### Data Validation
- **Pydantic** <2 - Data validation using Python type annotations
- **email-validator** 2.0.0+ - Email validation for Pydantic

### Configuration
- **python-dotenv** 1.0.0+ - Environment variable management
- **python-multipart** 0.0.20 - Required for file uploads (FastAPI)

### Why These Technologies?

**FastAPI:**
- Automatic API documentation (Swagger UI & ReDoc)
- Built-in async support
- Type hints for better IDE support
- Fast performance (comparable to NodeJS and Go)

**SQLAlchemy 2.0:**
- Modern async/await syntax
- Type-safe queries
- Advanced ORM features
- PostgreSQL-specific optimizations

**PostgreSQL:**
- ACID compliance
- Advanced data types (JSON, arrays, etc.)
- Excellent for relational data
- Industry-standard reliability

**Pydantic:**
- Automatic validation
- Clear error messages
- IDE auto-completion
- JSON schema generation

## 🤝 Contributing

### For Team Collaboration

**1. Before Pushing Your Changes:**
- Review [PUSH_CHECKLIST.md](PUSH_CHECKLIST.md) before every push
- Ensure `.env` is NOT in your commit (verify with `git status`)
- Clear Python cache: `Get-ChildItem -Recurse -Filter __pycache__ | Remove-Item -Recurse -Force`
- Test your changes locally

**2. Git Workflow:**

```bash
# Create a new branch for your feature
git checkout -b feature/your-feature-name

# Make your changes and test them

# Check what will be committed (make sure .env is NOT listed)
git status

# Add files
git add .

# Verify again
git status

# Commit with descriptive message
git commit -m "Add: Brief description of changes"

# Push to repository
git push origin feature/your-feature-name

# Create Pull Request on GitHub/GitLab
```

**3. Branch Naming Convention:**
- `feature/` - New features (e.g., `feature/add-sports-api`)
- `bugfix/` - Bug fixes (e.g., `bugfix/fix-user-validation`)
- `hotfix/` - Urgent fixes (e.g., `hotfix/database-connection`)
- `docs/` - Documentation updates (e.g., `docs/update-readme`)

**4. Commit Message Guidelines:**
- Use present tense: "Add feature" not "Added feature"
- Be descriptive but concise
- Examples:
  - `Add: Sports model and CRUD endpoints`
  - `Fix: User email validation error`
  - `Update: Database connection pool settings`
  - `Docs: Add API usage examples`

### For New Team Members 

When you join the project:

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EduSportsConnect-FastApi
   ```

2. **Setup your environment** (follow steps 2-6 above)
   - Create virtual environment
   - Install dependencies
   - Copy .env.example to .env
   - Configure with YOUR local database credentials
   - Create database
   - Run application

3. **Verify setup**
   - Visit http://localhost:8000/docs
   - Test the /db-test endpoint
   - Create a test user via API docs

4. **Start contributing**
   - Create a feature branch
   - Make changes
   - Submit pull request

## 📝 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `APP_NAME` | Application name | EduSportsConnect API |
| `APP_VERSION` | API version | 1.0.0 |
| `DEBUG` | Debug mode (dev only) | True |
| `DATABASE_URL` | PostgreSQL connection URL | postgresql+asyncpg://user:pass@localhost:5432/db |
| `DATABASE_ECHO` | Log SQL queries | True |
| `DATABASE_POOL_SIZE` | Connection pool size | 5 |
| `DATABASE_MAX_OVERFLOW` | Max overflow connections | 10 |
| `ALLOWED_ORIGINS` | CORS allowed origins | http://localhost:3000 |
| `SECRET_KEY` | JWT secret key | random-secret-key |

## 🔒 Security Notes

### Critical Security Practices

**1. Environment Variables**
- ✅ **DO**: Keep credentials in `.env` (ignored by git)
- ❌ **DON'T**: Hardcode credentials in source code
- ✅ **DO**: Use `.env.example` as a template for team
- ❌ **DON'T**: Commit `.env` file to repository

**2. Secret Key**
- Change `SECRET_KEY` in production
- Generate secure key: `openssl rand -hex 32`
- Never reuse keys across environments
- Rotate keys periodically

**3. Database Security**
- Use strong passwords (12+ characters, mixed case, numbers, symbols)
- Limit database user permissions
- Use connection pooling limits
- Enable SSL for production databases

**4. Production Checklist**
- [ ] Set `DEBUG=False`
- [ ] Use environment-specific `.env` files
- [ ] Enable HTTPS/TLS
- [ ] Set up proper CORS origins (don't use `*`)
- [ ] Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)
- [ ] Regular security audits: `pip install safety; safety check`
- [ ] Keep dependencies updated: `pip list --outdated`

### What NOT to Commit

```bash
# These are in .gitignore - NEVER commit them:
.env                    # Contains real credentials
venv/                   # Virtual environment
__pycache__/            # Python cache
*.pyc, *.pyo           # Compiled Python
.vscode/               # IDE settings
.idea/                 # PyCharm settings
*.db, *.sqlite         # Database files
*.log                  # Log files
```

### Verify Before Push

```bash
# Check what will be committed
git status

# Ensure .env is NOT listed
git check-ignore .env
# Should output: .env

# Search for potential secrets in code
git grep -i "password\|secret\|key" -- ':!.env.example' ':!README.md'
```

## 🚀 Deploying to Production

### Environment Setup

**1. Server Requirements**
- Python 3.10+
- PostgreSQL 12+
- 1GB+ RAM
- Reverse proxy (Nginx/Caddy)

**2. Production .env**
```env
DEBUG=False
DATABASE_URL=postgresql+asyncpg://user:password@db-server:5432/prod_db
ALLOWED_ORIGINS=https://yourdomain.com
SECRET_KEY=<generated-secure-key>
```

**3. Run with Gunicorn (Recommended)**
```bash
# Install
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**4. Use Process Manager**
```bash
# Using systemd (Linux)
sudo nano /etc/systemd/system/edusports.service

# Or use supervisor, pm2, or docker
```

**5. Setup Nginx Reverse Proxy**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Deployment Platforms

- **Docker**: Create Dockerfile and docker-compose.yml
- **Heroku**: Needs Procfile and runtime.txt
- **AWS**: EC2, RDS, Elastic Beanstalk
- **DigitalOcean**: App Platform or Droplet
- **Railway**: Simple deployment with PostgreSQL addon
- **Render**: Easy deployment with managed database

## � Environment Variables Reference

Complete list of all environment variables:

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `APP_NAME` | string | No | EduSportsConnect API | Application display name |
| `APP_VERSION` | string | No | 1.0.0 | API version number |
| `DEBUG` | boolean | No | True | Debug mode (disable in production) |
| `DATABASE_URL` | string | **Yes** | None | PostgreSQL async connection URL |
| `DATABASE_ECHO` | boolean | No | True | Log SQL queries to console |
| `DATABASE_POOL_SIZE` | integer | No | 5 | Connection pool size |
| `DATABASE_MAX_OVERFLOW` | integer | No | 10 | Max overflow connections |
| `ALLOWED_ORIGINS` | string | **Yes** | Empty | Comma-separated CORS origins |
| `SECRET_KEY` | string | **Yes** | None | Secret key for security |

## 🐳 Docker & GitHub Container Registry (GHCR)

### Build Docker image locally

```bash
docker build -t remote-fastapi-testing:latest .
```

### Run container locally

```bash
docker run --env-file .env -p 8000:8000 remote-fastapi-testing:latest
```

### Push image to GHCR automatically

A GitHub Actions workflow is included at `.github/workflows/docker-publish.yml`.

- Triggered on push to `main`, tags like `v1.0.0`, or manual run
- Publishes image to `ghcr.io/<owner>/<repo>`

### One-time GitHub setup

1. Go to repository **Settings → Actions → General**.
2. Ensure workflow permissions allow **Read and write permissions**.
3. Push your code to `main`.

After workflow success, pull the image using:

```bash
docker pull ghcr.io/<owner>/<repo>:main
```

## 📖 Additional Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/) - Framework documentation
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/) - ORM guide
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [PostgreSQL](https://www.postgresql.org/docs/) - Database manual

### Project Files
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Detailed architecture guide
- [PUSH_CHECKLIST.md](PUSH_CHECKLIST.md) - Pre-push verification
- `.env.example` - Environment template

## 🎯 Quick Start Checklist

- [ ] Python 3.10+ and PostgreSQL installed
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created and configured
- [ ] Database created in PostgreSQL
- [ ] Application runs successfully
- [ ] Can access http://localhost:8000/docs

## 📄 License

[Add your license information here]

## 👥 Team

[Add team member information here]

## 📞 Support

For issues or questions:
- Create an issue in the repository
- Check documentation and troubleshooting sections
- Contact: [Add contact information]

---

<div align="center">

**⭐ If this helps you, consider starring the repository!**

**Made with ❤️ for educational sports management**

**Happy Coding! 🚀**

</div>