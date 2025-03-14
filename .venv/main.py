from fastapi import FastAPI,Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List

from sqlalchemy.orm import Session
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL,connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False,bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

class UserResponse(BaseModel):
    name: str
    email: str

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/user/",response_model=UserResponse)
def create_user(user: UserResponse,db: Session=Depends(get_db)):
    db_user = User(name=user.name,email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/user/",response_model=List[UserResponse])
def read_user(skip: int =0, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).all()
    return users

@app.get("/")
def root():
    return {"Hello": "World"}

