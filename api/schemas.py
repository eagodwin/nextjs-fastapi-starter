from pydantic import BaseModel

class ExerciseBase(BaseModel):
  name: str
  target_muscles: str
  type: str
  equipment: str
  mechanics: str
  force: str
  experience_level: str
  secondary_muscles: str
  popularity: int

class ExerciseCreate(ExerciseBase):
  pass

class ExerciseResponse(ExerciseBase):
  primary_key: int
  name: str
  target_muscles: str
  type: str
  equipment: str
  mechanics: str
  force: str
  experience_level: str
  secondary_muscles: str
  rank: float
  similarity: float
  popularity: int
  class Config:
    orm_mode = True