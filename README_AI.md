# README_AI.md — AI Continuation Memory
> Update this file after EVERY change made.

---

## 1. PROJECT OVERVIEW

- **Business:** AutoPrime
- **Purpose:** Engine and transmission sales website. Customers browse crate engines, pullouts, LS swap packages and transmissions, add to cart and place orders. Owner receives email for every order.
- **Stack:** FastAPI (Python) + Plain HTML/CSS/Vanilla JS (no React/Vue)
- **Owner Email:** Configured in `.env` as `OWNER_EMAIL`
- **Admin URL:** `/admin`

---

## 2. ARCHITECTURE

```
project/
├── backend/
│   ├── __init__.py
│   ├── main.py           ← FastAPI app, CORS, routes, static files
│   ├── database.py       ← SQLAlchemy SQLite setup, get_db
│   ├── models.py         ← Booking, Order ORM models
│   ├── schemas.py        ← Pydantic v2 schemas
│   └── routes/
│       ├── __init__.py
│       ├── bookings.py   ← POST /api/bookings/
│       ├── orders.py     ← POST /api/orders/
│       └── admin.py      ← /api/admin/* (HTTP Basic Auth)
│   └── services/
│       ├── __init__.py
│       └── email.py      ← 4 async email functions (aiosmtplib)
├── frontend/
│   ├── index.html        ← Complete store (CSS + JS inline)
│   ├── products.js       ← PRODUCTS array (30+ items)
│   ├── admin.html        ← Admin dashboard
│   └── about.html        ← About page
├── .env                  ← Secrets (never commit)
├── .env.example
├── .gitignore
├── requirements.txt
└── README_AI.md
```

---

## 3. BACKEND DETAILS

### Routes
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/bookings/ | Create quote request, emails sent in background |
| POST | /api/orders/ | Create order, emails sent in background |
| GET | /api/admin/stats | Stats: totals/pending counts |
| GET | /api/admin/bookings | All quotes (newest first) |
| GET | /api/admin/bookings/{id} | Single quote |
| PATCH | /api/admin/bookings/{id} | Update status/notes |
| DELETE | /api/admin/bookings/{id} | Delete quote |
| GET | /api/admin/orders | All orders (newest first) |
| GET | /api/admin/orders/{id} | Single order |
| PATCH | /api/admin/orders/{id} | Update status/notes |
| DELETE | /api/admin/orders/{id} | Delete order |
| GET | / | Serves frontend/index.html |
| GET | /admin | Serves frontend/admin.html |
| GET | /about | Serves frontend/about.html |

### DB Models
- **Booking**: id, first_name, last_name, phone, email, service, vehicle_interest, details, status, created_at, notes
- **Order**: id, first_name, last_name, phone, email, company, address, city, state, zip, country, freight_region, contact_pref, best_time, notes, items (JSON string), total, payment_method, status, created_at

### Email Functions (services/email.py)
1. `send_customer_confirmation(booking)` — Confirms quote to customer
2. `send_owner_notification(booking)` — Alerts owner of new quote
3. `send_order_customer_confirmation(customer, items, total, shipping)` — Order confirmation with items table
4. `send_order_owner_notification(customer, items, total, shipping)` — Owner alert with full order

All wrapped in try/except — email failure never crashes submission.

---

## 4. FRONTEND DETAILS

### JS Functions (index.html)
| Function | Description |
|----------|-------------|
| `applyFilters()` | Filters PRODUCTS by all state vars, renders grid |
| `fuzzyMatch(query, product)` | Levenshtein fuzzy search across name/brand/fuel/category/year/transmission |
| `renderGrid(products)` | Renders product cards |
| `openModal(id)` | Opens product detail modal |
| `addToCart(id)` | Adds product to cart, shows toast |
| `openCart()` | Opens full-page cart overlay, sets #cart hash |
| `renderCart()` | Renders cart table + order summary |
| `submitOrder(e)` | POSTs to /api/orders, clears cart on success |
| `openQuote()` / `openQuoteForProduct(id)` | Opens quote modal (pre-fills if product) |
| `submitQuote(e)` | POSTs to /api/bookings/ |
| `setupAC(inputId, dropId)` | Wires autocomplete dropdown to search input |
| `doSearch(src)` | Applies nav/hero search to state and filters |

### Product Schema (products.js)
```js
{ id, name, brand, category, year, fuel, transmission, mileage, price, originalPrice, description, features[], inStock, badge, image, imageSearch }
```

### Cart Rules
- Stored in `localStorage` key `ac_cart`
- Free shipping: subtotal >= $5,000. Otherwise $500 flat.
- International: freight region overrides domestic shipping price.
- Hash `#cart` re-opens cart on page load.

### Search Tolerance
- query ≤ 2 chars → 0 errors (exact)
- query ≤ 4 chars → 1 error
- query > 4 chars → 2 errors

### Toast
- Bottom-LEFT corner (not right — chatbot on right)
- 3-second auto-dismiss
- Includes "View Cart" button

---

## 5. CURRENT STATE

### Working
- Full FastAPI backend with all routes
- SQLite database with Booking and Order models
- Pydantic v2 schemas
- Email service (aiosmtplib, STARTTLS, 4 HTML email functions)
- Admin HTTP Basic Auth
- templates/ — storefront pages (base, index, products, product_detail, checkout)
- backend/seed_data.py — 33 products across engine/transmission
- frontend/admin.html — full dashboard with login, stats, tabs, detail modal, auto-refresh
- frontend/about.html — about page

### Incomplete / To Configure
- `.env` needs real SMTP credentials
- Admin password should be changed before deployment
- Real product images (currently using Unsplash)
- Deploy to Hostinger VPS

---

## 6. DEPLOYMENT

- **VPS:** Hostinger VPS (Ubuntu)
- **Domain:** Namecheap
- **GitHub:** Private repo
- **Run command:** `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
- **Working directory:** project root
- **Env file:** Create `.env` manually on VPS (never commit)
- **Update live:** `git pull && systemctl restart autoprime` (or kill/restart uvicorn)

---

## 7. DEVELOPMENT RULES

- Do NOT break existing features
- Do NOT add JS frameworks (no React, Vue, etc.)
- Do NOT push `.env` or `*.db` to GitHub
- After every change: `git add . && git commit -m "..." && git push`
- Test mobile after every UI change
- Keep `products.js` as single source of product truth
- Admin auth is HTTP Basic Auth (credentials in `.env`)
- Emails use aiosmtplib async — never block requests
- Pydantic v2: use `.model_dump()` not `.dict()`

---

## 8. NEXT PRIORITIES

1. Fill in real `.env` credentials (SMTP, admin password)
2. Replace Unsplash placeholder images with real product photos
3. Update business contact info (phone, email, address) in index.html and about.html
4. Set up systemd service on VPS for auto-restart
5. Configure Nginx reverse proxy on VPS (port 80/443 → 8000)
6. Add SSL certificate (Let's Encrypt / Certbot)
7. Set up private GitHub repo and push code
8. Test full order flow end-to-end on VPS

---

## 9. LAST UPDATE

**Date:** 2026-05-10
**Changes:** Initial full build — all files created from scratch
**Reason:** New project setup per full specification
**Files:**
- backend/__init__.py
- backend/main.py
- backend/database.py
- backend/models.py
- backend/schemas.py
- backend/routes/__init__.py
- backend/routes/bookings.py
- backend/routes/orders.py
- backend/routes/admin.py
- backend/services/__init__.py
- backend/services/email.py
- frontend/index.html
- frontend/products.js
- frontend/admin.html
- frontend/about.html
- .env
- .env.example
- .gitignore
- requirements.txt
- README_AI.md
