from pydantic import BaseModel
class SpecimenOutput(BaseModel):
    id:int
    code:str
    cohort_id:int
    material:str
    enrolled_at:str
    followup_id:int
    entry_hours:float
    duration_hours:float
    event_observed:bool
    note:str
