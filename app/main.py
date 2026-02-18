from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import children, assessments
from .init_db import init_db

app = FastAPI(title="Anganwadi Early Screening API", version="0.1.0")

# ✅ CORS MUST COME BEFORE ROUTERS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Routers AFTER middleware
app.include_router(children.router, prefix="/api/v1")
app.include_router(assessments.router, prefix="/api/v1")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
