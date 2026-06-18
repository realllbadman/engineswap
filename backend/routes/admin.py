import os
import secrets
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import Order
from backend.schemas import OrderOut, OrderUpdate
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
security = HTTPBasic()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")


def require_auth(credentials: HTTPBasicCredentials = Depends(security)):
    ok_user = secrets.compare_digest(credentials.username.encode(), ADMIN_USERNAME.encode())
    ok_pass = secrets.compare_digest(credentials.password.encode(), ADMIN_PASSWORD.encode())
    if not (ok_user and ok_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), _=Depends(require_auth)):
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return {
        "total_orders": db.query(Order).count(),
        "pending_orders": db.query(Order).filter(Order.status == "pending").count(),
        "orders_month": db.query(Order).filter(Order.created_at >= month_start).count(),
    }


@router.get("/orders", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db), _=Depends(require_auth)):
    return db.query(Order).order_by(Order.created_at.desc()).all()


@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), _=Depends(require_auth)):
    o = db.query(Order).get(order_id)
    if not o:
        raise HTTPException(404, "Not found")
    return o


@router.patch("/orders/{order_id}", response_model=OrderOut)
def update_order(order_id: int, payload: OrderUpdate, db: Session = Depends(get_db), _=Depends(require_auth)):
    o = db.query(Order).get(order_id)
    if not o:
        raise HTTPException(404, "Not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(o, k, v)
    db.commit()
    db.refresh(o)
    return o


@router.delete("/orders/{order_id}", status_code=204)
def delete_order(order_id: int, db: Session = Depends(get_db), _=Depends(require_auth)):
    o = db.query(Order).get(order_id)
    if not o:
        raise HTTPException(404, "Not found")
    db.delete(o)
    db.commit()
