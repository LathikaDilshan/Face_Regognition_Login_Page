from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON

from db.database import Base


class attend(Base):
    __tablename__ = 'attends'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    attend_date = Column(DateTime, index=True)
    attend_time = Column(DateTime, index=True)
    position = Column(String, index=True)