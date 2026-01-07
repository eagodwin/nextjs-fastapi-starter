import json
from typing import Any, Optional
from pydantic import BaseModel, field_validator

class ExerciseBase(BaseModel):
  name: str
  target_muscles: str
  type: str
  equipment: str
  mechanics: str
  force_type: str
  experience_level: str
  secondary_muscles: str
  popularity: int

class ExerciseCreate(ExerciseBase):
  pass

class AnatomySchema(BaseModel):
  primary_muscle: str
  specific_head: Optional[str]
  length_bias: Optional[str]

class BiomechanicalProfileSchema(BaseModel):
  force_profile: str
  stability: str
  plane_of_motion: str

class ExecutionSchema(BaseModel):
  step_by_step_instructions: list[str]
  technical_cues: list[str]
  common_errors: list[str]

class ExerciseResponse(ExerciseBase):
  primary_key: int
  name: str
  target_muscles: str
  type: str
  equipment: str
  mechanics: str
  force_type: str
  experience_level: str
  secondary_muscles: str
  rank: float
  similarity: float
  popularity: int
  anatomical_precision: Optional[AnatomySchema]
  biomechanical_profile: Optional[BiomechanicalProfileSchema]
  execution: Optional[ExecutionSchema]
  # This is the magic part
  @field_validator('anatomical_precision', 'biomechanical_profile', 'execution', mode='before')
  @classmethod
  def ensure_dict(cls, v: Any) -> Any:
      if isinstance(v, str):
          try:
              return json.loads(v)
          except (json.JSONDecodeError, TypeError):
              return v
      return v

