import datetime
from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    extracted_text = Column(String)
    summary = Column(String) # Stores the English summary
    translation = Column(String, nullable=True) # Stores the translated summary if requested
    created_at = Column(DateTime, default=datetime.datetime.utcnow)