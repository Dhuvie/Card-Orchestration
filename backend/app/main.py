from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat_routes import router as chat_router

app = FastAPI(title="Visiting Card API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "alive"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
