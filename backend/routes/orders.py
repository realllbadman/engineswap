import json
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Order
from backend.schemas import OrderCreate, OrderOut
from backend.services.email import send_order_customer_confirmation, send_order_owner_notification

router = APIRouter()


@router.post("/", response_model=OrderOut, status_code=201)
async def create_order(
    order_in: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    items_dicts = [item.model_dump() for item in order_in.items]
    subtotal = sum(i["unit_price"] * i["quantity"] for i in items_dicts)
    shipping = 0.0 if subtotal >= 5000 else 500.0

    if order_in.freight_region:
        freight_map = {
            "Canada/Mexico": 800, "Caribbean/Central America": 900,
            "South America": 1000, "Europe": 1200,
            "Middle East/North Africa": 1100, "Sub-Saharan Africa": 1300,
            "Asia Pacific": 1400, "Australia/New Zealand": 1500, "Other": 1600,
        }
        shipping = freight_map.get(order_in.freight_region, 1600)

    data = order_in.model_dump()
    data["items"] = json.dumps(items_dicts)
    data["total"] = order_in.total

    order = Order(**data)
    db.add(order)
    db.commit()
    db.refresh(order)

    customer = {k: v for k, v in data.items() if k not in ("items", "total")}
    background_tasks.add_task(send_order_customer_confirmation, customer, items_dicts, order_in.total, shipping)
    background_tasks.add_task(send_order_owner_notification, customer, items_dicts, order_in.total, shipping)
    return order
