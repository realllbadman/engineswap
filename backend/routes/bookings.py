from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Booking
from backend.schemas import BookingCreate, BookingOut
from backend.services.email import send_customer_confirmation, send_owner_notification

router = APIRouter()


@router.post("/", response_model=BookingOut, status_code=201)
async def create_booking(
    booking_in: BookingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    booking = Booking(**booking_in.model_dump())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    background_tasks.add_task(send_customer_confirmation, booking)
    background_tasks.add_task(send_owner_notification, booking)
    return booking
