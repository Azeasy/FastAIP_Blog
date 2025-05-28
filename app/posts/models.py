from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="posts")
