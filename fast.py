from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from pydantic import BaseModel  # Import Pydantic's BaseModel

# SQLAlchemy Setup
DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Define SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Define Pydantic model for response
class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime

# FastAPI Setup
app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create Endpoint
@app.post("/tasks/", response_model=TaskResponse)  # Use TaskResponse as the response model
def create_task(task_details: dict, db: Session = Depends(get_db)):
    new_task = Task(**task_details)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# Read Endpoint
@app.get("/tasks/{task_id}", response_model=TaskResponse)  # Use TaskResponse as the response model
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Update Endpoint
@app.put("/tasks/{task_id}", response_model=TaskResponse)  # Use TaskResponse as the response model
def update_task(task_id: int, updated_task: TaskResponse, db: Session = Depends(get_db)):
    existing_task = db.query(Task).filter(Task.id == task_id).first()
    if existing_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update task attributes using the values from the Pydantic model
    existing_task.title = updated_task.title
    existing_task.description = updated_task.description
    existing_task.completed = updated_task.completed

    db.commit()
    db.refresh(existing_task)
    return existing_task

# Delete Endpoint
@app.delete("/tasks/{task_id}", response_model=dict)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}
