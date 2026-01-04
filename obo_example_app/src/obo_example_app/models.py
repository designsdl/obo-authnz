from sqlalchemy import Column, Integer, String, Text
from .database import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(String, index=True) # The "User" this note belongs to
    content = Column(Text)
