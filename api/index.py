from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, MetaData, func, text
from sqlalchemy.orm import sessionmaker, Session
from .models import Base, Exercise
from .schemas import ExerciseCreate, ExerciseResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import logging

load_dotenv()
TEMBO_DB_URL = os.getenv('TEMBO_DB_URL')
if not TEMBO_DB_URL:
    raise ValueError("DATABASE_URL_UNPOOLED is not set in the environment variables.")

engine = create_engine(TEMBO_DB_URL, connect_args={"sslmode":"require"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
  # Startup: Print out all tables
  metadata = MetaData()
  metadata.reflect(bind=engine, schema='public')
  print("Tables in the database:")
  print(metadata.tables.keys())

  # Allow the app to run
  yield

  # Shutdown (if needed, you can add cleanup code here)
  print("Shutting down the app")


app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


@app.get('/')
def read_root():
  return {"message": "Hello, FastAPI connected to Tembo DB on Replit!"}


@app.get("/api/py/exercises")
async def get_exercises(skip: int = 0,
                        limit: int = 10,
                        db: Session = Depends(get_db)):
  return {"message": db.query(Exercise).offset(skip).limit(limit).all()}


@app.get("/api/py/exercises/autocomplete", response_model=list[ExerciseResponse])
def autocomplete_exercises(name: str, db: Session = Depends(get_db)):
    results = db.query(
        Exercise.primary_key,
        Exercise.name,
        Exercise.target_muscles,
        Exercise.type,
        Exercise.equipment,
        Exercise.mechanics,
        Exercise.force,
        Exercise.experience_level,
        Exercise.secondary_muscles,
    ).filter(Exercise.name.ilike(f"%{name}%")).all()
    exercises = [
          ExerciseResponse(
              primary_key=primary_key,
              name=name,
              target_muscles=target_muscles,
              type=type,
              equipment=equipment,
              mechanics=mechanics,
              force=force,
              experience_level=experience_level,
              secondary_muscles=secondary_muscles,
              rank=0,
              similarity=0
          )
          for primary_key, name, target_muscles, type, equipment, mechanics, force, experience_level, secondary_muscles in results
    ]
    return exercises

#Exercise search by name using pgsql fts magic combined with fuzzy search
@app.get("/api/py/exercises/name", response_model=list[ExerciseResponse])
def get_exercises_by_name(name: str = '', db: Session = Depends(get_db)):
  try:
    if name == '':
      query = db.query(Exercise)
      exercises = query.all()
      return exercises
    else:
      tsquery_name = ' & '.join(name.split())
      query = db.query(
          Exercise.primary_key,
          Exercise.name,
          Exercise.target_muscles,
          Exercise.type,
          Exercise.equipment,
          Exercise.mechanics,
          Exercise.force,
          Exercise.experience_level,
          Exercise.secondary_muscles,
          func.ts_rank_cd(func.to_tsvector(Exercise.name), func.to_tsquery(tsquery_name)).label('rank'),
          func.similarity(Exercise.name, name).label('similarity')
      ).filter(
          func.to_tsvector(Exercise.name).op('@@')(func.to_tsquery(tsquery_name)) |
          Exercise.name.op('%')(name)
      ).order_by(
          text('rank DESC'), text('similarity DESC')
      )

      # Execute the query
      results = query.all()

      # Transform the results into ExerciseResponse format
      exercises = [
          ExerciseResponse(
              primary_key=primary_key,
              name=name,
              target_muscles=target_muscles,
              type=type,
              equipment=equipment,
              mechanics=mechanics,
              force=force,
              experience_level=experience_level,
              secondary_muscles=secondary_muscles,
              rank=rank,
              similarity=similarity
          )
          for primary_key, name, target_muscles, type, equipment, mechanics, force, experience_level, secondary_muscles, rank,  similarity in results
      ]

      return exercises
  except Exception as e:
      logging.error(f"Error querying database: {e}")
      raise HTTPException(status_code=500, detail="Database error")
    


@app.get("/api/py/exercises/{primary_key}", response_model=ExerciseResponse)
def get_exercise(primary_key: int, db: Session = Depends(get_db)):
  exercise = db.query(Exercise).filter(
      Exercise.primary_key == primary_key).first()
  if not exercise:
    raise HTTPException(status_code=404, detail="Exercise not found")
  return exercise


@app.post("/api/py/exercises/", response_model=ExerciseResponse)
def create_exercise(exercise: ExerciseCreate, db: Session = Depends(get_db)):
  new_exercise = Exercise(name=exercise.name,
                          target_muscles=exercise.target_muscles,
                          type=exercise.type,
                          equipment=exercise.equipment,
                          mechanics=exercise.mechanics,
                          force=exercise.force,
                          experience_level=exercise.experience_level,
                          secondary_muscles=exercise.secondary_muscles)
  db.add(new_exercise)
  db.commit()
  db.refresh(new_exercise)
  return new_exercise


if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=3000)
