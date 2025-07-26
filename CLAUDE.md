# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BiliNote is an AI-powered video note-taking assistant that supports extracting content from video platforms (Bilibili, YouTube, Douyin, etc.) and generating structured Markdown notes using AI models. It consists of a FastAPI backend and a React/Vite frontend.

## Development Commands

### Frontend (React/Vite)
```bash
cd BillNote_frontend
pnpm install           # Install dependencies
pnpm dev              # Start development server (http://localhost:5173)
pnpm build            # Build for production
pnpm lint             # Run ESLint
pnpm preview          # Preview production build
```

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt  # Install dependencies
python main.py                   # Start development server (http://localhost:8483)
```

### Full Stack Development
1. Start backend: `cd backend && python main.py`
2. Start frontend: `cd BillNote_frontend && pnpm dev`
3. Access application at `http://localhost:5173`

### Docker Deployment
```bash
docker-compose up -d     # Standard deployment
docker-compose -f docker-compose.gpu.yml up -d  # GPU-accelerated deployment
```

## Code Architecture

### Backend Structure
- **FastAPI App**: Main application in `backend/main.py` with CORS middleware and static file serving
- **Router Architecture**: API routes organized in `app/routers/` (note, provider, model, config)
- **Database Layer**: SQLAlchemy models and DAOs in `app/db/` with SQLite storage
- **Service Layer**: Core business logic in `app/services/`
- **AI Integration**: GPT providers in `app/gpt/` supporting OpenAI, DeepSeek, Qwen, and custom models
- **Media Processing**: Video downloaders in `app/downloaders/` for different platforms
- **Audio Transcription**: Multiple transcription providers in `app/transcriber/`

### Frontend Structure
- **React Router**: Multi-page application with nested routing
- **State Management**: Zustand stores for task management (`src/store/taskStore/`)
- **Component Architecture**: Reusable components in `src/components/`
- **Page Components**: Main pages in `src/pages/` (HomePage, SettingPage, etc.)
- **Service Layer**: API communication in `src/services/`
- **UI Library**: Tailwind CSS with Radix UI components

### Key Integration Points
- **Task Management**: Frontend Zustand store syncs with backend via polling (`useTaskPolling` hook)
- **Backend Health Check**: `useCheckBackend` hook ensures backend availability
- **File Handling**: Static files served from backend for screenshots and uploads

### Data Flow
1. User submits video URL through frontend form
2. Backend downloads video and extracts audio
3. Transcription service converts audio to text
4. AI model generates structured notes from transcript
5. Frontend polls for task updates and displays results

## Dependencies

### Critical System Dependencies
- **FFmpeg**: Required for audio/video processing - must be in system PATH
- **Python 3.8+**: Backend runtime
- **Node.js/pnpm**: Frontend package management

### Backend Key Libraries
- FastAPI, SQLAlchemy, faster-whisper, yt-dlp, openai
- Platform-specific downloaders for Bilibili, YouTube, Douyin

### Frontend Key Libraries
- React 19, Zustand, React Router, Tailwind CSS, Radix UI
- Markdown rendering with react-markdown and syntax highlighting

## Development Notes

### Environment Configuration
- Backend configuration via `.env` file (copy from `.env.example`)
- Frontend development server auto-proxies to backend
- CORS configured for localhost and Tauri origins

### Task Processing Pipeline
- Tasks flow through: PENDING → RUNNING → SUCCESS/FAILED
- Each task includes: video download, transcription, AI note generation
- Results stored in `backend/note_results/` with JSON metadata

### Testing
- No test framework currently configured
- Manual testing required for video processing pipelines

## Common Workflows

### Adding New Video Platform Support
1. Create downloader class in `app/downloaders/` inheriting from `BaseDownloader`
2. Register in downloader factory
3. Add platform-specific URL validation

### Adding New AI Model Provider
1. Implement GPT class in `app/gpt/` inheriting from `BaseGPT`
2. Register in `gpt_factory.py`
3. Add provider configuration in database

### Debugging Task Failures
- Check backend logs in `backend/logs/app.log`
- Examine task status files in `note_results/`
- Verify FFmpeg installation and system dependencies