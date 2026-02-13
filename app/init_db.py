from __future__ import annotations

from .db import engine
from .models import Base
from app.models import child, assessment   # 👈 ADD THIS LINE

def init_db():
    Base.metadata.create_all(bind=engine)