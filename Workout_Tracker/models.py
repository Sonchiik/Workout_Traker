import enum
from sqlalchemy import Column, Enum, Integer, String, ForeignKey, Boolean, Float, DateTime
from database import Base
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    workout_plan = relationship("Workout_Plan", back_populates="user")
    
class MuscleGroupEnum(enum.Enum):
    chest = 'chest'
    back = 'back'
    legs = 'legs'
    hands = 'hands'
    shoulders = 'shoulders'
    
class CategoryEnum(enum.Enum):
    cardio = 'cardio'
    strength = 'strength'
    flexibility = 'flexibility'
    
class StatusEnum(enum.Enum):
    pending = 'pending'
    completed = 'completed'
    skipped = 'skipped'
    
class Exercise(Base):
    __tablename__ = 'exercises'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)    
    description = Column(String(500), nullable=True)
    category = Column(Enum(CategoryEnum), nullable=False)
    muscle_category = Column(Enum(MuscleGroupEnum), nullable=False)
    
    workout_exercise = relationship("Workout_Exercises", back_populates="exercise", cascade="all, delete-orphan")
    
class Workout_Plan(Base):
    __tablename__ = 'workout_plan'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    schedule = Column(DateTime, nullable=True)
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.pending)
    
    workout_exercise = relationship("Workout_Exercises", back_populates="workout_plan")
    user = relationship("Users", back_populates="workout_plan")
    
class Workout_Exercises(Base):
    __tablename__ = 'workout_exercises'
    
    id = Column(Integer, primary_key=True)
    workout_plan_id = Column(Integer, ForeignKey('workout_plan.id'), nullable=False)
    exercise_id = Column(Integer, ForeignKey('exercises.id'), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    
    workout_plan = relationship("Workout_Plan", back_populates="workout_exercise")
    exercise = relationship("Exercise", back_populates="workout_exercise")