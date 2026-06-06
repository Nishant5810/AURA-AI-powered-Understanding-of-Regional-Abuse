import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from app.database import Base

class FlaggedContent(Base):
    __tablename__ = "flagged_content"

    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(Text, nullable=False)
    processed_text = Column(Text, nullable=True)
    detected_language = Column(String(50), nullable=False)
    label = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    severity = Column(String(50), nullable=False)
    target_community = Column(String(100), nullable=True, default="General")
    reasoning = Column(Text, nullable=True)
    toxic_phrases = Column(Text, nullable=True)  # JSON-serialized list of strings or dicts
    suggested_action = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class EmergingSlang(Base):
    __tablename__ = "emerging_slang"

    id = Column(Integer, primary_key=True, index=True)
    term = Column(String(100), unique=True, index=True, nullable=False)
    language = Column(String(50), nullable=False)
    definition = Column(Text, nullable=True)
    frequency = Column(Integer, default=1)
    growth_rate = Column(Float, default=0.0)  # Percentage growth (e.g. 230.0 for +230%)
    status = Column(String(50), default="New")  # "New", "Monitored", "Blocked"
    first_seen = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)

class RegionalTrend(Base):
    __tablename__ = "regional_trends"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String(100), nullable=False)
    language = Column(String(50), nullable=False)
    toxic_count = Column(Integer, default=0)
    non_toxic_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
