from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, func, or_, select

from app.database import get_session
from app.models import User, UserCreate, UserList, UserRead, UserUpdate, utcnow

router = APIRouter(prefix="/users", tags=["users"])
SessionDep = Annotated[Session, Depends(get_session)]


def _get_or_404(session: Session, user_id: int) -> User:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"User {user_id} not found")
    return user


def _ensure_email_free(session: Session, email: str, exclude_id: Optional[int] = None) -> None:
    stmt = select(User).where(User.email == email)
    if exclude_id is not None:
        stmt = stmt.where(User.id != exclude_id)
    if session.exec(stmt).first():
        raise HTTPException(status.HTTP_409_CONFLICT, f"Email {email} already exists")


def _commit(session: Session, user: User) -> User:
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already exists")
    session.refresh(user)
    return user


@router.get("", response_model=UserList)
def list_users(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    q: Optional[str] = Query(None, description="Search in name or email"),
    is_active: Optional[bool] = None,
):
    stmt = select(User)
    count_stmt = select(func.count()).select_from(User)
    if q:
        cond = or_(col(User.name).ilike(f"%{q}%"), col(User.email).ilike(f"%{q}%"))
        stmt, count_stmt = stmt.where(cond), count_stmt.where(cond)
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
        count_stmt = count_stmt.where(User.is_active == is_active)

    total = session.exec(count_stmt).one()
    items = session.exec(stmt.order_by(col(User.id)).offset(skip).limit(limit)).all()
    return {"total": total, "skip": skip, "limit": limit, "items": items}


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: SessionDep):
    return _get_or_404(session, user_id)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, session: SessionDep):
    email = str(user_in.email).lower()
    _ensure_email_free(session, email)
    user = User(**user_in.model_dump(exclude={"email"}), email=email)
    return _commit(session, user)


@router.put("/{user_id}", response_model=UserRead)
def replace_user(user_id: int, user_in: UserCreate, session: SessionDep):
    user = _get_or_404(session, user_id)
    email = str(user_in.email).lower()
    _ensure_email_free(session, email, exclude_id=user_id)
    for key, value in user_in.model_dump(exclude={"email"}).items():
        setattr(user, key, value)
    user.email = email
    user.updated_at = utcnow()
    return _commit(session, user)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_in: UserUpdate, session: SessionDep):
    user = _get_or_404(session, user_id)
    data = user_in.model_dump(exclude_unset=True)
    if "email" in data:
        if data["email"] is None:
            raise HTTPException(422, "email cannot be null")
        data["email"] = str(data["email"]).lower()
        _ensure_email_free(session, data["email"], exclude_id=user_id)
    for key in ("name", "is_active"):
        if key in data and data[key] is None:
            raise HTTPException(422, f"{key} cannot be null")
    for key, value in data.items():
        setattr(user, key, value)
    user.updated_at = utcnow()
    return _commit(session, user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: SessionDep):
    user = _get_or_404(session, user_id)
    session.delete(user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
