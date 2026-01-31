# 🚀 Todo Full-Stack Chatbot App

A modern, AI-powered todo application with natural language task management, built with Next.js, FastAPI, and Groq LLM.

![Next.js](https://img.shields.io/badge/Next.js-16.1.2-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-blue)
![Groq](https://img.shields.io/badge/Groq-LLM-orange)

## ✨ Features

### 🤖 AI-Powered Chatbot
- **Natural Language Task Management**: Create, complete, and delete tasks using conversational commands
- **Smart Date Parsing**: Understands phrases like "tomorrow", "next Friday", "in 3 days"
- **Auto-Categorization**: Automatically categorizes tasks (work, personal, shopping, health, etc.)
- **Priority Suggestions**: Suggests priority levels based on task content
- **Task Breakdown**: Suggests subtasks for complex tasks
- **Productivity Insights**: Shows completion rates, overdue tasks, and category breakdowns

### 🎨 Modern UI
- **Dark Mode**: Full dark mode support with system preference detection
- **Skeleton Loaders**: Smooth loading states with shimmer animations
- **Completion Animations**: Satisfying bounce and checkmark animations
- **iOS-Style Filters**: Modern segmented control for task filtering
- **Debounced Search**: Optimized search with 300ms delay
- **Responsive Design**: Works seamlessly on mobile and desktop

### 🔐 Authentication & Security
- ✅ User authentication (signup/signin) with JWT tokens
- ✅ Secure password hashing with bcrypt
- ✅ User-specific task isolation
- ✅ Protected API routes
- ✅ CORS protection

### 📊 Task Management
- ✅ Create, read, update, and delete tasks
- ✅ Mark tasks as complete/incomplete
- ✅ Filter by status (all, active, completed)
- ✅ Search tasks by title
- ✅ Priority levels (urgent, high, medium, low)
- ✅ Categories (work, personal, shopping, health, finance, home, education)
- ✅ Due dates with natural language parsing

## 🛠️ Technology Stack

### Frontend
- **Next.js 16.1.2** - React framework with App Router and Turbopack
- **TypeScript** - Type-safe development
- **Tailwind CSS v4** - Modern utility-first styling
- **Better Auth** - Authentication library with JWT
- **React Hooks** - State management

### Backend
- **FastAPI 0.109+** - Modern Python web framework
- **SQLModel 0.0.14+** - SQL database ORM
- **Neon PostgreSQL** - Serverless PostgreSQL database
- **JWT** - JSON Web Tokens for authentication (python-jose)
- **Bcrypt** - Password hashing (passlib)
- **Alembic 1.13+** - Database migrations

### AI & Tools
- **Groq** - Fast LLM inference provider
- **Model**: llama-3.3-70b-versatile
- **MCP Tools** - Model Context Protocol for function calling
- **Natural Language Processing** - Custom date parsing and categorization

## 📁 Project Structure

```
.
├── frontend/                  # Next.js frontend application
│   ├── app/                  # App Router pages
│   ├── components/           # React components
│   │   ├── auth/            # Authentication components
│   │   ├── layout/          # Layout components (Header, ThemeToggle)
│   │   ├── tasks/           # Task components (TaskList, TaskItem, TaskFilters)
│   │   └── FloatingChatWidget.tsx  # AI chatbot widget
│   ├── lib/                 # Utilities and API client
│   └── public/              # Static assets
├── backend/                  # FastAPI backend application
│   ├── src/
│   │   ├── agents/          # Groq AI agent
│   │   ├── api/             # API routes (auth, tasks, chat)
│   │   ├── mcp_tools/       # MCP function calling tools
│   │   ├── models/          # SQLModel database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic & AI enhancements
│   │   └── core/            # Core utilities (config, security)
│   └── alembic/             # Database migrations
├── specs/                    # Feature specifications
├── vercel.json              # Vercel deployment configuration
└── README.md                # This file
```

## 📦 Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL database (Neon account recommended)
- Groq API key (free at https://console.groq.com/keys)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
DATABASE_URL=your_neon_database_url
JWT_SECRET=your_secret_key_here
GROQ_API_KEY=your_groq_api_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=168
```

**Generate JWT_SECRET**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Get Groq API Key**: Visit https://console.groq.com/keys (free tier available)

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the backend server:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

The backend will be available at `http://localhost:8001`
API documentation: `http://localhost:8001/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file:
```bash
cp .env.example .env.local
```

Edit `.env.local` and add your configuration:
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_JWT_SECRET=same_as_backend_jwt_secret
BETTER_AUTH_SECRET=your_better_auth_secret_here
```

**Generate BETTER_AUTH_SECRET**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Important**: `NEXT_PUBLIC_JWT_SECRET` must match the `JWT_SECRET` in your backend `.env` file.

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🚀 Deployment

### Deploy Frontend to Vercel

1. **Push to GitHub** (already done ✅)

2. **Import to Vercel**:
   - Go to https://vercel.com/new
   - Click "Import Project"
   - Select your GitHub repository: `Todo-FullStack-Chatbot-App`
   - **Important**: Set the root directory to `frontend`

3. **Configure Build Settings**:
   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

4. **Add Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.com
   NEXT_PUBLIC_JWT_SECRET=your_jwt_secret_here
   BETTER_AUTH_SECRET=your_better_auth_secret_here
   ```

5. **Deploy**: Click "Deploy" and wait for the build to complete

### Deploy Backend (Options)

#### Option 1: Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
cd backend
railway init
railway up

# Add environment variables in Railway dashboard:
# - DATABASE_URL
# - JWT_SECRET
# - GROQ_API_KEY
```

#### Option 2: Render
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set root directory to `backend`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables (DATABASE_URL, JWT_SECRET, GROQ_API_KEY)
7. Deploy

#### Option 3: Fly.io
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
cd backend
fly launch
fly deploy

# Set environment variables
fly secrets set DATABASE_URL=your_database_url
fly secrets set JWT_SECRET=your_jwt_secret
fly secrets set GROQ_API_KEY=your_groq_api_key
```

### After Deployment

1. Update `NEXT_PUBLIC_API_URL` in Vercel to point to your deployed backend
2. Redeploy the frontend
3. Test the application at your Vercel URL

## 🎯 Usage Examples

### Chatbot Commands

Once you're signed in, click the floating chat button (bottom-right) and try these commands:

**Create Tasks**:
- "Create task to buy groceries"
- "Add task to submit report by Friday"
- "Create urgent task to call mom"
- "Add task to exercise tomorrow at 6pm"

**List Tasks**:
- "Show my tasks"
- "List all tasks"
- "What are my tasks?"
- "Show my list"

**Complete Tasks**:
- "Complete task 1"
- "Mark task 2 as done"
- "Complete task buy groceries"
- "Finish task call mom"

**Delete Tasks**:
- "Delete task 3"
- "Remove task call mom"
- "Delete all completed tasks"

**Insights & Stats**:
- "Show my stats"
- "How am I doing?"
- "Show productivity insights"
- "What's my completion rate?"

### UI Features

**Dark Mode**:
- Click the theme toggle in the header (☀️/🌙/💻)
- Choose light, dark, or system preference

**Task Filtering**:
- Use the segmented control to filter: All / Active / Completed
- Search tasks using the search bar (debounced for performance)

**Task Management**:
- Click checkbox to complete/uncomplete tasks
- Click task card to view details
- Use the "+" button to create new tasks manually

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

### API Endpoints

**Authentication**:
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/signin` - Sign in and get JWT token

**Tasks**:
- `GET /api/tasks` - Get all tasks for authenticated user
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/{task_id}` - Get a specific task
- `PUT /api/tasks/{task_id}` - Update a task
- `DELETE /api/tasks/{task_id}` - Delete a task
- `POST /api/tasks/{task_id}/toggle` - Toggle task completion status

**Chat**:
- `POST /api/chat` - Send message to AI chatbot
- `GET /api/chat/conversations` - Get user's conversation history

## 🔒 Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT token-based authentication
- ✅ User-specific data isolation
- ✅ CORS protection
- ✅ SQL injection prevention with SQLModel
- ✅ Environment variable protection
- ✅ Secure API key management

## 🛠️ Development Workflow

This project follows the Spec-Driven Development (SDD) workflow:
1. Write feature specifications
2. Generate architectural plans
3. Break down into testable tasks
4. Implement via Claude Code with specialized agents

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License

## 🙏 Acknowledgments

- Built with [Next.js](https://nextjs.org/)
- Powered by [Groq](https://groq.com/) for fast LLM inference
- Database hosted on [Neon](https://neon.tech/)
- UI components inspired by modern design patterns

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ using Claude Code and Groq AI**
