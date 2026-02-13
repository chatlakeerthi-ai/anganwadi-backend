from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import children, assessments
from .init_db import init_db   # ✅ ADD THIS

app = FastAPI(title="Anganwadi Early Screening API", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(children.router, prefix="/api/v1")
app.include_router(assessments.router, prefix="/api/v1")


# ✅ ADD THIS BLOCK
@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
