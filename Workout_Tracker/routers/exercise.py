from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from typing import Annotated
from database import SessionLocal
from sqlalchemy.orm import Session
from models import Exercise, MuscleGroupEnum, CategoryEnum
from pydantic import BaseModel
from .auth import get_current_user


router = APIRouter(
    prefix="/exercises",
    tags=['exercises']
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        
user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]

class ExerciseRequest(BaseModel):
    name: str    
    description: str
    category: CategoryEnum
    muscle_category: MuscleGroupEnum
    
class ExerciseResponce(BaseModel):
    id: int
    name: str    
    description: str
    category: CategoryEnum
    muscle_category: MuscleGroupEnum
    
    class Config:
        from_attributes = True


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_exercise(db: db_dependency):
    exercises= db.query(Exercise).all()
    
    if not exercises:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    return exercises

@router.get("/{exercise_id}", status_code=status.HTTP_200_OK)
async def get_exercise(db: db_dependency, exercise_id: int):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    return exercise

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_exercise(user: user_dependency, db: db_dependency, exercise: ExerciseRequest):
    if not user or user.get('is_admin', False) != 1:
        raise HTTPException(status_code=403, detail="You don't have permission to create")
    
    exsisting_exercise = db.query(Exercise).filter(Exercise.name == exercise.name).first()
    
    if exsisting_exercise:
        raise HTTPException(status_code=400, detail="Exercise with this name already exists")

    new_exercise = Exercise(**exercise.model_dump())

    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)
    
    return new_exercise
    
@router.delete("/{exercise_id}", status_code=status.HTTP_200_OK)
async def delete_exercise(user: user_dependency, db: db_dependency, exercise_id: int):
    if not user or user.get('is_admin', False) != 1:
        raise HTTPException(status_code=403, detail="You do not have permission to delete")
    
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    db.delete(exercise)
    db.commit()
    
    return {"message": "Exercise deleted successfully"}

@router.put("/{exercise_id}", status_code=status.HTTP_200_OK)
async def update_exercise(user: user_dependency, db: db_dependency, exercise_id: int, exercise_request: ExerciseRequest):
    if not user or user.get('is_admin', False) != 1:
        raise HTTPException(status_code=403, detail="You do not have permission to update")
    
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    exercise.name = exercise_request.name
    exercise.description = exercise_request.description
    exercise.category = exercise_request.category
    exercise.muscle_category = exercise_request.muscle_category
    
    db.commit()
    db.refresh(exercise)
    
    return exercise

