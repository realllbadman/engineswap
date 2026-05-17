import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from contextlib import asynccontextmanager
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.database import engine, Base, SessionLocal
from backend.routes import bookings, orders, admin
from backend.models import Product
from backend.seed_data import PRODUCTS_SEED

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR   = os.path.join(BASE_DIR, "static")


def sync_products(db: Session) -> None:
    """Upsert every product from seed_data into the DB.
    - Existing products: all fields updated (image, price, name, etc.)
    - New products: inserted fresh.
    - Products removed from seed_data: deleted from DB.
    """
    seed_slugs = {p["slug"] for p in PRODUCTS_SEED}

    # Delete any products no longer in seed_data
    db.query(Product).filter(Product.slug.notin_(seed_slugs)).delete(synchronize_session=False)

    for p in PRODUCTS_SEED:
        existing = db.query(Product).filter(Product.slug == p["slug"]).first()
        fields = dict(
            slug=p["slug"],
            name=p["name"],
            brand=p["brand"],
            category=p["category"],
            year=p.get("year"),
            fuel=p.get("fuel"),
            transmission=p.get("transmission"),
            mileage=p.get("mileage", 0),
            price=p["price"],
            original_price=p.get("original_price"),
            description=p.get("description", ""),
            features=json.dumps(p.get("features", [])),
            in_stock=1 if p.get("in_stock", True) else 0,
            badge=p.get("badge"),
            image=p.get("image", ""),
        )
        if existing:
            for k, v in fields.items():
                setattr(existing, k, v)
        else:
            db.add(Product(**fields))

    db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        sync_products(db)   # always sync — picks up any edits to seed_data.py
    finally:
        db.close()
    yield


app = FastAPI(title="EngineSwap Autos API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (new static/ dir — CSS, JS, images)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

_jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    cache_size=0,  # disable LRU cache — fixes unhashable dict TypeError on Python 3.12
)
templates = Jinja2Templates(env=_jinja_env)

# ── existing API routes (unchanged) ──────────────────────────────
app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(orders.router,   prefix="/api/orders",   tags=["orders"])
app.include_router(admin.router,    prefix="/api/admin",    tags=["admin"])


# ── storefront pages ─────────────────────────────────────────────
@app.get("/")
def index(request: Request):
    db = SessionLocal()
    try:
        # Featured: 4 cars first row, 4 engines second row
        _car_cats  = ("sedan", "suv", "truck", "sports")
        cars_feat  = (db.query(Product)
                      .filter(Product.in_stock == 1, Product.category.in_(_car_cats))
                      .limit(4).all())
        eng_feat   = (db.query(Product)
                      .filter(Product.in_stock == 1, Product.category == "engine")
                      .limit(4).all())
        featured   = cars_feat + eng_feat
        brand_rows = (
            db.query(Product.brand, func.count(Product.id))
            .group_by(Product.brand)
            .order_by(func.count(Product.id).desc())
            .all()
        )
        total = db.query(Product).count()
        return templates.TemplateResponse(request, "index.html", {
            "products": featured,
            "brand_counts": brand_rows,
            "total_count": total,
        })
    finally:
        db.close()


def _interleave_products(products):
    """Return products in cycling order: engines → cars → transmissions → repeat.
    When a category filter is active the list is passed through unchanged."""
    engines  = [p for p in products if p.category == "engine"]
    vehicles = [p for p in products if p.category in ("sedan","suv","truck","sports")]
    trans    = [p for p in products if p.category == "transmission"]

    # Only interleave when showing the full mix; pure-category views stay as-is
    if not (engines and vehicles) and not (engines and trans) and not (vehicles and trans):
        return products   # single-category view — no interleaving needed

    result, ie, iv, it = [], 0, 0, 0
    chunk = 3  # one grid row per category
    while ie < len(engines) or iv < len(vehicles) or it < len(trans):
        result.extend(engines[ie:ie+chunk]);  ie += chunk
        result.extend(vehicles[iv:iv+chunk]); iv += chunk
        result.extend(trans[it:it+chunk]);    it += chunk
    return result


@app.get("/products")
def products_page(request: Request, q: str = "", category: str = ""):
    db = SessionLocal()
    try:
        query = db.query(Product).order_by(Product.in_stock.desc(), Product.price.asc())
        all_products = query.all()

        # Apply interleave only on the unfiltered view; JS handles live filtering
        ordered = _interleave_products(all_products)

        total = db.query(Product).count()
        return templates.TemplateResponse(request, "products.html", {
            "products": ordered,
            "q": q,
            "category": category,
            "total_count": total,
        })
    finally:
        db.close()


@app.get("/products/{slug}")
def product_detail(request: Request, slug: str):
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.slug == slug).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        features = json.loads(product.features) if product.features else []
        related  = (
            db.query(Product)
            .filter(Product.category == product.category, Product.slug != slug)
            .limit(4).all()
        )
        return templates.TemplateResponse(request, "product_detail.html", {
            "product": product,
            "features": features,
            "related": related,
        })
    finally:
        db.close()


@app.get("/checkout")
def checkout_page(request: Request):
    return templates.TemplateResponse(request, "checkout.html", {})


# ── kept pages (FileResponse) ────────────────────────────────────
@app.get("/admin")
def admin_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "admin.html"))


@app.get("/about")
def about_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "about.html"))
