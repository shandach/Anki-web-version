from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, decks, cards, study, stats, quiz

app = FastAPI(title="Anki Web API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://anki-web-version.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(decks.router)
app.include_router(cards.router)
app.include_router(study.router)
app.include_router(stats.router)
app.include_router(quiz.router)

@app.get("/")
def root():
    return {"message": "Anki Web API"}

@app.get("/health")
def health():
    return {"status": "ok"}
