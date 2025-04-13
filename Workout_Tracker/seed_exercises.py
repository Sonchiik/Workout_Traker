from sqlalchemy.orm import Session
from models import Exercise
from database import SessionLocal

exercise_data = [
    {
        "name": "Bench Press",
        "description": "Strengthens chest and triceps.",
        "category": "strength",
        "muscle_category": "chest"
    },
    {
        "name": "Deadlift",
        "description": "Works the back, glutes, and legs.",
        "category": "strength",
        "muscle_category": "back"
    },
    {
        "name": "Squats",
        "description": "Fundamental leg strength exercise.",
        "category": "strength",
        "muscle_category": "legs"
    },
    {
        "name": "Overhead Press",
        "description": "Strengthens shoulders and upper chest.",
        "category": "strength",
        "muscle_category": "shoulders"
    },
    {
        "name": "Bicep Curl",
        "description": "Isolates and builds biceps.",
        "category": "strength",
        "muscle_category": "hands"
    },
    {
        "name": "Tricep Extension",
        "description": "Targets triceps muscle.",
        "category": "strength",
        "muscle_category": "hands"
    },
    {
        "name": "Running",
        "description": "Improves endurance and leg strength.",
        "category": "cardio",
        "muscle_category": "legs"
    },
    {
        "name": "Cycling",
        "description": "Low-impact cardio workout for legs.",
        "category": "cardio",
        "muscle_category": "legs"
    },
    {
        "name": "Jump Rope",
        "description": "Cardio exercise for legs and coordination.",
        "category": "cardio",
        "muscle_category": "legs"
    },
    {
        "name": "Rowing Machine",
        "description": "Full-body cardio emphasizing the back.",
        "category": "cardio",
        "muscle_category": "back"
    },
    {
        "name": "Shoulder Stretch",
        "description": "Improves shoulder flexibility.",
        "category": "flexibility",
        "muscle_category": "shoulders"
    },
    {
        "name": "Hamstring Stretch",
        "description": "Enhances flexibility in legs and lower back.",
        "category": "flexibility",
        "muscle_category": "legs"
    },
    {
        "name": "Neck Rolls",
        "description": "Relieves tension in neck and shoulders.",
        "category": "flexibility",
        "muscle_category": "shoulders"
    },
    {
        "name": "Cat-Cow Stretch",
        "description": "Improves flexibility of the spine.",
        "category": "flexibility",
        "muscle_category": "back"
    },
]

def seed_exercise():
    db: Session = SessionLocal()
    for data in exercise_data:
        existing_exercise = db.query(Exercise).filter(Exercise.name == data['name']).first()
        if not existing_exercise:
            exercise = Exercise(**data)
            db.add(exercise)
    db.commit()
    db.close()
    print("Exercises seeded successfully")
    
if __name__ == "__main__":
    seed_exercise()