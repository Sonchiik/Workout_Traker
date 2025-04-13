from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from typing import Annotated
from database import SessionLocal
from sqlalchemy.orm import Session
from models import Workout_Plan, StatusEnum
from pydantic import BaseModel, field_validator
from .auth import get_current_user
from datetime import datetime


router = APIRouter(
    prefix="/workout_plan",
    tags=['workout_plan']
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class UpdateWorkoutTime(BaseModel):        
    schedule: datetime 
    
    @field_validator('schedule', mode='before')
    def parse_schedule(cls, v):
        try:
           return datetime.strptime(v, '%d-%m-%Y %H:%M') 
        except ValueError:
            raise ValueError('Invalid data, should be DD-MM-YYYY HH:MM')
        
class WorkoutPlanRequest(UpdateWorkoutTime):
    status: StatusEnum
    
class UpdateWorkoutStatus(BaseModel):        
    status: StatusEnum 
        
         
user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]

def get_user_plan(user, plan_id, db):
    plan = db.query(Workout_Plan).filter(Workout_Plan.user_id == user.get('user_id'))\
    .filter(Workout_Plan.id == plan_id).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return plan


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_workout_plan(user: user_dependency, db: db_dependency, plan: WorkoutPlanRequest):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    user_plan = Workout_Plan(**plan.model_dump(), user_id = user.get('user_id'))
    
    db.add(user_plan)
    db.commit()
    db.refresh(user_plan)
    
    return user_plan 
    
@router.get('/', status_code=status.HTTP_200_OK)
async def get_all_plan(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    plans = db.query(Workout_Plan).filter(Workout_Plan.user_id == user.get('user_id')).all()
    
    if not plans:
        raise HTTPException(status_code=404, detail="Plans not found")
    
    return plans

@router.get('/{plan_id}', status_code=status.HTTP_200_OK)
async def get_plan_by_id(user: user_dependency, db: db_dependency, plan_id: int):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    plan = get_user_plan(user, plan_id, db)
    
    return plan

@router.delete('/{plan_id}', status_code=status.HTTP_200_OK)
async def delete_plan(user: user_dependency, db: db_dependency, plan_id: int):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    plan = get_user_plan(user, plan_id, db)
    
    db.delete(plan)
    db.commit()
    
    return {"message": "Workout plan deleted successfully"}

@router.patch('/{plan_id}/schedule', status_code=status.HTTP_200_OK)
async def change_workout_time(user: user_dependency, db: db_dependency, plan_id: int, plan_updated: UpdateWorkoutTime):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    plan = get_user_plan(user, plan_id, db)
    
    plan.schedule = plan_updated.schedule
    
    db.commit()
    db.refresh(plan)
    
    return plan

@router.patch('/{plan_id}/status', status_code=status.HTTP_200_OK)
async def change_workout_status(user: user_dependency, db: db_dependency, plan_id: int, status_update: UpdateWorkoutStatus):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    plan = get_user_plan(user, plan_id, db)
    
    plan.status = status_update.status
    
    db.commit()
    db.refresh(plan)
    
    return plan