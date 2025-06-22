# Book-My-Event 🎟️

Mini-Calendly full-stack demo  
**Front-end:** React + Vite + Tailwind  
**Back-end:** FastAPI / SQLModel / Celery

| Live Demo | Repo |
|-----------|------|
| **FE** https://bookmyevent.vercel.app | https://github.com/<you>/book-my-event |
| **API** https://api.bookmyevent.xyz/docs | —

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
