from sqlalchemy import Column , Integer , String , DateTime , Boolean , ForeignKey , JSON


from db.database import Base

class users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True , index = True)
    username = Column(String , index = True)
    email = Column(String , index = True)
    position = Column(String, index=True)
    password = Column(String)
