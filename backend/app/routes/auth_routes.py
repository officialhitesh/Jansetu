from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.schemas.user_schema import UserRegister, UserLogin, UserResponse
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register", response_model=UserResponse)
def register(data: UserRegister):
    db: Session = SessionLocal()

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        full_name=data.full_name,
        email=data.email,
        password=hash_password(data.password),
        role=data.role or "user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()

    return new_user


@router.post("/login")
def login(data: UserLogin):
    db: Session = SessionLocal()

    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        db.close()
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # If role is provided, verify it matches (used by admin login)
    if data.role and data.role != user.role:
        db.close()
        raise HTTPException(
            status_code=403,
            detail="Access denied. Role mismatch."
        )

    token = create_access_token({"sub": user.email})

    response = {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role
        }
    }

    db.close()
    return response
