---
title: Todo Backend API with AI Chatbot
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# 🤖 Todo Backend API with AI Chatbot

FastAPI backend for the Todo Full-Stack Chatbot App with AI-powered task management, JWT authentication, and PostgreSQL database.

## 🚀 Live API

- **API Base URL**: https://ayeshamasood110-todo-backend-chatbot.hf.space
- **Swagger UI**: https://ayeshamasood110-todo-backend-chatbot.hf.space/docs
- **ReDoc**: https://ayeshamasood110-todo-backend-chatbot.hf.space/redoc
- **Health Check**: https://ayeshamasood110-todo-backend-chatbot.hf.space/health

## ✨ Features

- 🤖 **AI-Powered Chatbot**: Natural language task management with Groq LLM
- 📝 **RESTful API**: Complete task management endpoints
- 🔐 **JWT Authentication**: Secure user authentication
- 🗄️ **PostgreSQL Database**: SQLModel ORM with Neon Serverless
- 🔒 **Password Hashing**: Bcrypt for secure password storage
- 🌐 **CORS Configuration**: Frontend integration support
- 🔄 **Auto Migrations**: Alembic database migrations
- 🧠 **AI Enhancements**: Smart date parsing, auto-categorization, priority suggestions

## 🔐 Environment Variables Required

Configure these in Space Settings → Repository secrets:

- `DATABASE_URL` - PostgreSQL connection string (Neon Serverless)
- `JWT_SECRET` - Secret key for JWT token generation
- `JWT_ALGORITHM` - JWT algorithm (default: HS256)
- `JWT_EXPIRATION_HOURS` - Token expiration time (default: 168 hours = 7 days)
- `GROQ_API_KEY` - Groq API key for AI chatbot (get free at https://console.groq.com/keys)
- `FRONTEND_URL` - Your Vercel frontend URL for CORS (optional)

## 📚 API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/signin` - Sign in and get JWT token

### Tasks (Protected - Requires JWT)
- `GET /api/tasks` - Get all tasks for authenticated user
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/{task_id}` - Get a specific task
- `PUT /api/tasks/{task_id}` - Update a task
- `DELETE /api/tasks/{task_id}` - Delete a task
- `POST /api/tasks/{task_id}/toggle` - Toggle task completion status

### Chat (Protected - Requires JWT)
- `POST /api/chat` - Send message to AI chatbot
- `GET /api/chat/conversations` - Get user's conversation history

### Health
- `GET /health` - Check API health status
- `GET /` - API information

## 🛠️ Technology Stack

- **Framework**: FastAPI 0.109+
- **ORM**: SQLModel 0.0.14+
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: JWT (python-jose)
- **Password Hashing**: Bcrypt (passlib)
- **Migrations**: Alembic 1.13+
- **AI**: Groq LLM (llama-3.3-70b-versatile)
- **Deployment**: Docker on Hugging Face Spaces

## 🔗 Related Links

- **Frontend**: https://your-vercel-app.vercel.app
- **GitHub Repository**: https://github.com/ArifAbbas11/Todo-FullStack-Chatbot-App
- **Documentation**: See `/docs` endpoint for interactive API documentation

## 📝 License

MIT License - See LICENSE file for details

---

Built with ❤️ using FastAPI, Groq AI, and deployed on Hugging Face Spaces

