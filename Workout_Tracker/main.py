from fastapi import FastAPI
from models import Users, Workout_Exercises, Workout_Plan, Exercise
from database import Base, engine
from routers import exercise, auth, workout_plan, wourkout_exercise

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(exercise.router)
app.include_router(auth.router)
app.include_router(workout_plan.router)
app.include_router(wourkout_exercise.router)