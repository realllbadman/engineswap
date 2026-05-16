from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class BookingCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str
    service: Optional[str] = "General Inquiry"
    vehicle_interest: Optional[str] = None
    details: Optional[str] = None


class BookingUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class BookingOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: str
    email: str
    service: Optional[str]
    vehicle_interest: Optional[str]
    details: Optional[str]
    status: str
    created_at: datetime
    notes: Optional[str]

    model_config = {"from_attributes": True}


class OrderItem(BaseModel):
    product_id: str
    name: str
    year: int
    fuel: str
    unit_price: float
    quantity: int


class OrderCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str
    company: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    freight_region: Optional[str] = None
    contact_pref: Optional[str] = None
    best_time: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItem]
    total: float
    payment_method: Optional[str] = None


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class OrderOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: str
    email: str
    company: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip: Optional[str]
    country: Optional[str]
    freight_region: Optional[str]
    contact_pref: Optional[str]
    best_time: Optional[str]
    notes: Optional[str]
    items: str
    total: float
    payment_method: Optional[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
