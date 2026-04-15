from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.runner_profile import RunnerProfile
from ..schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from ..services.deps import get_current_user_id

router = APIRouter()


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    body: ProfileCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    existing = db.query(RunnerProfile).filter(RunnerProfile.user_id == current_user_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Perfil já existe — use PUT para atualizar")

    profile = RunnerProfile(user_id=current_user_id, **body.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("", response_model=ProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    profile = db.query(RunnerProfile).filter(RunnerProfile.user_id == current_user_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado — crie com POST /profile")
    return profile


@router.put("", response_model=ProfileResponse)
def update_profile(
    body: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    profile = db.query(RunnerProfile).filter(RunnerProfile.user_id == current_user_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado — crie com POST /profile")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile
