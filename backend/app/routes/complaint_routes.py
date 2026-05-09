from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List, Optional

from app.database import SessionLocal
from app.models.complaint import Complaint
from app.models.user import User
from app.schemas.complaint_schema import ComplaintCreate, ComplaintResponse
from app.utils.security import SECRET_KEY, ALGORITHM

from jose import jwt, JWTError

router = APIRouter(
    prefix="/complaints",
    tags=["Complaints"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Extract user from JWT token in Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.post("/", response_model=ComplaintResponse)
def create_complaint(
    complaint: ComplaintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_complaint = Complaint(
        user_id=current_user.id,        # FIX: was hardcoded to 1
        title=complaint.title,
        description=complaint.description,
        location=complaint.location,
        city=complaint.city,
        state=complaint.state,
        pin_code=complaint.pin_code,
        contact_number=complaint.contact_number,
        department="Pending AI Classification",
        urgency="Medium",
        sentiment="Neutral",
        status="Pending"
    )

    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)

    return new_complaint


@router.get("/my", response_model=List[ComplaintResponse])
def get_my_complaints(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all complaints filed by the logged-in user."""
    complaints = db.query(Complaint).filter(
        Complaint.user_id == current_user.id
    ).order_by(Complaint.id.desc()).all()

    return complaints


@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db)
):
    complaint = db.query(Complaint).filter(
        Complaint.id == complaint_id
    ).first()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    return complaint
