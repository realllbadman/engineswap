import json
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Text, Float, DateTime
from backend.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    phone = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    company = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    state = Column(Text, nullable=True)
    zip = Column(Text, nullable=True)
    country = Column(Text, nullable=True)
    freight_region = Column(Text, nullable=True)
    contact_pref = Column(Text, nullable=True)
    best_time = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    items = Column(Text, nullable=False)
    total = Column(Float, nullable=False)
    payment_method = Column(Text, nullable=True)
    status = Column(Text, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Product(Base):
    __tablename__ = "products"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    slug         = Column(Text, unique=True, nullable=False)
    name         = Column(Text, nullable=False)
    brand        = Column(Text, nullable=False)
    category     = Column(Text, nullable=False)   # engine | transmission
    year         = Column(Integer, nullable=True)
    fuel         = Column(Text, nullable=True)
    transmission = Column(Text, nullable=True)
    mileage      = Column(Integer, default=0)
    price        = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    description  = Column(Text, nullable=True)
    features     = Column(Text, nullable=True)    # JSON array string
    in_stock     = Column(Integer, default=1)     # 1 = True, 0 = False
    badge        = Column(Text, nullable=True)
    image        = Column(Text, nullable=True)

    @property
    def features_list(self):
        try:
            return json.loads(self.features) if self.features else []
        except Exception:
            return []

    @property
    def is_in_stock(self):
        return bool(self.in_stock)
