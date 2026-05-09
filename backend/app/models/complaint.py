from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)

    # User who submitted the complaint
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Complaint form fields
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    file_path = Column(String, nullable=True)

    location = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    pin_code = Column(String, nullable=False)
    contact_number = Column(String, nullable=False)

    # AI predictions
    department = Column(String, nullable=True)
    urgency = Column(String, nullable=True)
    sentiment = Column(String, nullable=True)

    # Complaint status
    status = Column(String, default="Pending")

    # Date and time
    created_at = Column(DateTime(timezone=True), server_default=func.now())
