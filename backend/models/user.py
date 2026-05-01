"""User model for authentication and account management."""
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base
import uuid


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # KYC verification
    is_superuser = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Profile
    pan_number = Column(String(10), nullable=True)  # For Indian KYC

    def __repr__(self):
        return f"<User {self.email}>"
