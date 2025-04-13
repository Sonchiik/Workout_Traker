from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from typing import Annotated, List
from database import SessionLocal
from sqlalchemy.orm import Session
from models import Workout_Exercises, Exercise, Workout_Plan
from pydantic import BaseModel, field_validator
from .auth import get_current_user
from datetime import datetime
from .exercise import ExerciseResponce


router = APIRouter(
    prefix="/workout_exercises",
    tags=['workout_exercises']
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        
class AddExerciseRequest(BaseModel):
    sets: int
    reps: int
    weight: float
         
class WorkoutExerciseResponce(BaseModel):
    id: int
    workout_plan_id: int
    sets: int
    reps: int
    weight: float
    exercise: ExerciseResponce

    class Config:
        from_attributes = True
    
    
user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=WorkoutExerciseResponce)
async def add_exercise(user: user_dependency, db: db_dependency, 
                       exercise_request: AddExerciseRequest, 
                       exercise_id: int, plan_id: int):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    workout_plan = db.query(Workout_Plan).filter(Workout_Plan.user_id == user.get('user_id'))\
        .filter(Workout_Plan.id == plan_id).first()
        
    if not workout_plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    
    new_exercise = Workout_Exercises(**exercise_request.model_dump(), workout_plan_id=workout_plan.id, exercise_id=exercise.id)
    
    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)
    
    return new_exercise

@router.get('/', response_model=List[WorkoutExerciseResponce], status_code=status.HTTP_200_OK)
async def get_all_exercise(user: user_dependency, db: db_dependency, plan_id: int):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    workout_plan = db.query(Workout_Plan).filter(Workout_Plan.user_id == user.get('user_id'))\
        .filter(Workout_Plan.id == plan_id).first()
        
    if not workout_plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    
    all_exercise = db.query(Workout_Exercises).filter(Workout_Exercises.workout_plan_id == workout_plan.id).all()
    
    return all_exercise

@router.delete('/{exercise_id}', status_code=status.HTTP_200_OK)
async def delete_exercise_from_plan(user: user_dependency, db: db_dependency,
                                    plan_id: int, exercise_id: int):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    workout_plan = db.query(Workout_Plan).filter(Workout_Plan.user_id == user.get('user_id'))\
        .filter(Workout_Plan.id == plan_id).first()
        
    if not workout_plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    
    exercise = db.query(Workout_Exercises).filter(Workout_Exercises.workout_plan_id == workout_plan.id)\
        .filter(Workout_Exercises.exercise_id == exercise_id).first()
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    db.delete(exercise)
    db.commit()
    
    return {"message": "exercise delete successfully"}
    