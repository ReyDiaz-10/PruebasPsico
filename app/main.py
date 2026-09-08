from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .auth import authenticate_admin, create_token, require_admin
from .database import Base, engine, get_db
from .models import Candidate, Vote, Voter
from .schemas import CandidateCreate, CandidateOut, CandidateStatistic, StatisticsOut, Token, VoteCreate, VoteOut, VoterCreate, VoterOut

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="PruebasPsico - Sistema de Votaciones", version="1.0.0", lifespan=lifespan)

def clean(value: str) -> str:
    return " ".join(value.strip().split())

def same_person_exists(db: Session, name: str, opposite_model) -> bool:
    return db.scalar(select(opposite_model.id).where(func.lower(opposite_model.name) == clean(name).lower())) is not None

@app.get("/health", tags=["Sistema"])
def health(): return {"status": "ok"}

@app.post("/auth/token", response_model=Token, tags=["Autenticación"])
def login(form: OAuth2PasswordRequestForm = Depends()):
    if not authenticate_admin(form.username, form.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {"access_token": create_token(form.username), "token_type": "bearer"}

@app.post("/voters", response_model=VoterOut, status_code=201, tags=["Votantes"])
def create_voter(data: VoterCreate, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    if same_person_exists(db, data.name, Candidate):
        raise HTTPException(409, "Esta persona ya está registrada como candidato")
    voter = Voter(name=clean(data.name), email=str(data.email).lower())
    db.add(voter)
    try: db.commit(); db.refresh(voter)
    except IntegrityError: db.rollback(); raise HTTPException(409, "El correo ya está registrado")
    return voter

@app.get("/voters", response_model=list[VoterOut], tags=["Votantes"])
def list_voters(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), _: str = Depends(require_admin)):
    return db.scalars(select(Voter).order_by(Voter.id).offset(skip).limit(limit)).all()

@app.get("/voters/{voter_id}", response_model=VoterOut, tags=["Votantes"])
def get_voter(voter_id: int, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    voter = db.get(Voter, voter_id)
    if not voter: raise HTTPException(404, "Votante no encontrado")
    return voter

@app.delete("/voters/{voter_id}", status_code=204, tags=["Votantes"])
def delete_voter(voter_id: int, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    voter = db.get(Voter, voter_id)
    if not voter: raise HTTPException(404, "Votante no encontrado")
    if voter.has_voted: raise HTTPException(409, "No se puede eliminar un votante que ya votó")
    db.delete(voter); db.commit(); return Response(status_code=204)

@app.post("/candidates", response_model=CandidateOut, status_code=201, tags=["Candidatos"])
def create_candidate(data: CandidateCreate, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    if same_person_exists(db, data.name, Voter):
        raise HTTPException(409, "Esta persona ya está registrada como votante")
    candidate = Candidate(name=clean(data.name), party=clean(data.party) if data.party else None)
    db.add(candidate)
    try: db.commit(); db.refresh(candidate)
    except IntegrityError: db.rollback(); raise HTTPException(409, "El candidato ya existe")
    return candidate

@app.get("/candidates", response_model=list[CandidateOut], tags=["Candidatos"])
def list_candidates(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    return db.scalars(select(Candidate).order_by(Candidate.id).offset(skip).limit(limit)).all()

@app.get("/candidates/{candidate_id}", response_model=CandidateOut, tags=["Candidatos"])
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.get(Candidate, candidate_id)
    if not candidate: raise HTTPException(404, "Candidato no encontrado")
    return candidate

@app.delete("/candidates/{candidate_id}", status_code=204, tags=["Candidatos"])
def delete_candidate(candidate_id: int, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    candidate = db.get(Candidate, candidate_id)
    if not candidate: raise HTTPException(404, "Candidato no encontrado")
    if candidate.votes: raise HTTPException(409, "No se puede eliminar un candidato con votos")
    db.delete(candidate); db.commit(); return Response(status_code=204)

@app.post("/votes", response_model=VoteOut, status_code=201, tags=["Votos"])
def cast_vote(data: VoteCreate, db: Session = Depends(get_db)):
    try:
        voter = db.execute(select(Voter).where(Voter.id == data.voter_id).with_for_update()).scalar_one_or_none()
        candidate = db.execute(select(Candidate).where(Candidate.id == data.candidate_id).with_for_update()).scalar_one_or_none()
        if not voter: raise HTTPException(404, "Votante no encontrado")
        if not candidate: raise HTTPException(404, "Candidato no encontrado")
        if voter.has_voted: raise HTTPException(409, "El votante ya emitió su voto")
        vote = Vote(voter_id=voter.id, candidate_id=candidate.id)
        voter.has_voted = True
        candidate.votes += 1
        db.add(vote); db.commit(); db.refresh(vote)
        return vote
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "El votante ya emitió su voto")

@app.get("/votes", response_model=list[VoteOut], tags=["Votos"])
def list_votes(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), _: str = Depends(require_admin)):
    return db.scalars(select(Vote).order_by(Vote.id).offset(skip).limit(limit)).all()

@app.get("/votes/statistics", response_model=StatisticsOut, tags=["Votos"])
def statistics(db: Session = Depends(get_db)):
    candidates = db.scalars(select(Candidate).order_by(Candidate.votes.desc(), Candidate.name)).all()
    total_votes = db.scalar(select(func.count(Vote.id))) or 0
    total_voters = db.scalar(select(func.count(Voter.id))) or 0
    # Funciones lambda pedidas en el ejercicio: transformación funcional de resultados.
    to_result = lambda c: CandidateStatistic(candidate_id=c.id, candidate_name=c.name, party=c.party, votes=c.votes, percentage=round((c.votes / total_votes * 100) if total_votes else 0, 2))
    results = list(map(to_result, candidates))
    return StatisticsOut(total_votes=total_votes, total_registered_voters=total_voters, total_voters_who_voted=total_votes, participation_percentage=round((total_votes / total_voters * 100) if total_voters else 0, 2), results=results)

