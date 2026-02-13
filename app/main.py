from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import children, assessments

app = FastAPI(title="Anganwadi Early Screening API", version="0.1.0")

# For local development with Flutter (Android emulator/web/desktop).
# Tighten this list for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(children.router, prefix="/api/v1")
app.include_router(assessments.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
