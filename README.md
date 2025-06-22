# Book-My-Event 🎟️

Mini-Calendly full-stack demo  
**Front-end:** React + Vite + Tailwind  
**Back-end:** FastAPI / SQLModel / Celery

| Live Demo | Repo |
|-----------|------|
| **FE** https://book-my-event-frp6jhrw0-vimlendu-sharmas-projects.vercel.app | https://github.com/VimlenduSharma/Book-my-event |
| **API** http://localhost:8080 | —

---

## Quick Start (Local)

```bash
git clone https://github.com/<you>/book-my-event
cd book-my-event
cp backend/.env.example backend/.env      # tweak secrets
cd backend && docker compose up --build
# open http://localhost:8000/docs  (API)
# open another terminal
cd ../frontend && npm i && npm run dev
# open http://localhost:8080
