from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class VoterCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr

class VoterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; name: str; email: EmailStr; has_voted: bool; created_at: datetime

class CandidateCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    party: str | None = Field(default=None, max_length=150)

class CandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; name: str; party: str | None; votes: int; created_at: datetime

class VoteCreate(BaseModel):
    voter_id: int = Field(gt=0)
    candidate_id: int = Field(gt=0)

class VoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; voter_id: int; candidate_id: int; created_at: datetime

class CandidateStatistic(BaseModel):
    candidate_id: int; candidate_name: str; party: str | None; votes: int; percentage: float

class StatisticsOut(BaseModel):
    total_votes: int; total_registered_voters: int; total_voters_who_voted: int
    participation_percentage: float; results: list[CandidateStatistic]

class Token(BaseModel):
    access_token: str; token_type: str

