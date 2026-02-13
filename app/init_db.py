from __future__ import annotations

from .db import engine
from .models import Base
import app.models

def init_db():
    Base.metadata.create_all(bind=engine)
