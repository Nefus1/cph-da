from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.domain import router as domain_router
from app.db.session import Base, engine
from app.models import models  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contract Platform API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(domain_router)


@app.get("/health")
def health():
    return {"status": "ok"}
