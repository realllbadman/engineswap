import os
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER", "")
# Google shows app passwords grouped with spaces — strip them before use
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").replace(" ", "")
OWNER_EMAIL   = os.getenv("OWNER_EMAIL", "")
BUSINESS_EMAIL= os.getenv("BUSINESS_EMAIL", "")
OWNER_PHONE   = os.getenv("OWNER_PHONE", "")
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "EngineSwap Autos")

ACCENT = "#e87722"   # EngineSwap orange
DARK   = "#1a2c4e"   # EngineSwap navy


def _base_html(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; background:#f5f5f5; margin:0; padding:0; }}
  .wrap {{ max-width:600px; margin:0 auto; background:#fff; }}
  .header {{ background:{DARK}; padding:24px 32px; }}
  .header h1 {{ color:#fff; margin:0; font-size:22px; }}
  .header span {{ color:{ACCENT}; }}
  .body {{ padding:32px; }}
  .body h2 {{ color:{DARK}; font-size:18px; margin-top:0; }}
  .row {{ border-bottom:1px solid #eee; padding:10px 0; display:flex; }}
  .row .label {{ color:#888; width:160px; flex-shrink:0; font-size:14px; }}
  .row .val {{ color:{DARK}; font-size:14px; font-weight:600; }}
  .footer {{ background:{DARK}; padding:16px 32px; text-align:center; }}
  .footer p {{ color:#888; font-size:12px; margin:0; }}
  .badge {{ display:inline-block; background:{ACCENT}; color:#fff; padding:4px 12px; border-radius:20px; font-size:13px; }}
  table.items {{ width:100%; border-collapse:collapse; margin:16px 0; }}
  table.items th {{ background:{DARK}; color:#fff; padding:8px 12px; text-align:left; font-size:13px; }}
  table.items td {{ padding:8px 12px; border-bottom:1px solid #eee; font-size:13px; }}
  .total-row td {{ font-weight:700; background:#f9f9f9; }}
</style></head>
<body><div class="wrap">
<div class="header"><h1>{BUSINESS_NAME} <span>|</span> {title}</h1></div>
<div class="body">{body}</div>
<div class="footer"><p>&copy; {BUSINESS_NAME} &mdash; All rights reserved</p></div>
</div></body></html>"""


async def _send(to: str, subject: str, html: str):
    if not SMTP_USER or not SMTP_PASSWORD:
        print("[email] SKIPPED — SMTP_USER or SMTP_PASSWORD not set in .env")
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{BUSINESS_NAME} <{SMTP_USER}>"
    msg["To"] = to
    msg.attach(MIMEText(html, "html"))
    print(f"[email] Sending '{subject}' to {to} via {SMTP_USER}")
    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASSWORD,
        start_tls=True,
    )
    print(f"[email] Sent OK → {to}")


async def send_customer_confirmation(booking):
    try:
        body = f"""
        <h2>We received your quote request!</h2>
        <p>Hi {booking.first_name}, thank you for reaching out to {BUSINESS_NAME}. Our team will contact you shortly.</p>
        <div class="row"><span class="label">Name</span><span class="val">{booking.first_name} {booking.last_name}</span></div>
        <div class="row"><span class="label">Phone</span><span class="val">{booking.phone}</span></div>
        <div class="row"><span class="label">Email</span><span class="val">{booking.email}</span></div>
        <div class="row"><span class="label">Service</span><span class="val">{booking.service or 'General Inquiry'}</span></div>
        <div class="row"><span class="label">Vehicle Interest</span><span class="val">{booking.vehicle_interest or '—'}</span></div>
        <div class="row"><span class="label">Details</span><span class="val">{booking.details or '—'}</span></div>
        <p style="margin-top:24px;">Questions? Call us: <strong>{OWNER_PHONE}</strong> or reply to this email.</p>
        """
        await _send(booking.email, f"Quote Request Received — {BUSINESS_NAME}", _base_html("Quote Received", body))
    except Exception as e:
        print(f"[email] customer confirmation failed: {e}")


async def send_owner_notification(booking):
    try:
        body = f"""
        <h2>New Quote Request <span class="badge">#{booking.id}</span></h2>
        <div class="row"><span class="label">Name</span><span class="val">{booking.first_name} {booking.last_name}</span></div>
        <div class="row"><span class="label">Phone</span><span class="val">{booking.phone}</span></div>
        <div class="row"><span class="label">Email</span><span class="val">{booking.email}</span></div>
        <div class="row"><span class="label">Service</span><span class="val">{booking.service or '—'}</span></div>
        <div class="row"><span class="label">Vehicle Interest</span><span class="val">{booking.vehicle_interest or '—'}</span></div>
        <div class="row"><span class="label">Details</span><span class="val">{booking.details or '—'}</span></div>
        <div class="row"><span class="label">Status</span><span class="val">{booking.status}</span></div>
        <p style="margin-top:24px;"><a href="https://engineswapautos.com/admin" style="background:{ACCENT};color:#fff;padding:10px 20px;text-decoration:none;border-radius:4px;">View in Admin Panel</a></p>
        """
        await _send(OWNER_EMAIL, f"[{BUSINESS_NAME}] New Quote — {booking.first_name} {booking.last_name}", _base_html("New Quote Request", body))
    except Exception as e:
        print(f"[email] owner notification failed: {e}")


async def send_order_customer_confirmation(customer, items, total, shipping):
    try:
        rows = "".join(
            f"<tr><td>{i['name']}</td><td>{i['year']} / {i['fuel']}</td><td>{i['quantity']}</td><td>${i['unit_price']:,.2f}</td><td>${i['unit_price']*i['quantity']:,.2f}</td></tr>"
            for i in items
        )
        ship_label = "Free" if shipping == 0 else f"${shipping:,.2f}"
        body = f"""
        <h2>Order Confirmed!</h2>
        <p>Hi {customer['first_name']}, your order has been received. We'll reach out to confirm payment and delivery details.</p>
        <table class="items">
          <thead><tr><th>Item</th><th>Spec</th><th>Qty</th><th>Unit Price</th><th>Subtotal</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
        <div class="row"><span class="label">Subtotal</span><span class="val">${(total - shipping):,.2f}</span></div>
        <div class="row"><span class="label">Shipping</span><span class="val">{ship_label}</span></div>
        <div class="row"><span class="label">Total</span><span class="val">${total:,.2f}</span></div>
        <p style="margin-top:24px;">Payment: <strong>{customer.get('payment_method','—')}</strong></p>
        <p>Questions? Call: <strong>{OWNER_PHONE}</strong></p>
        """
        await _send(customer["email"], f"Order Confirmation — {BUSINESS_NAME}", _base_html("Order Confirmed", body))
    except Exception as e:
        print(f"[email] order customer confirmation failed: {e}")


async def send_order_owner_notification(customer, items, total, shipping):
    try:
        rows = "".join(
            f"<tr><td>{i['name']}</td><td>{i['year']} / {i['fuel']}</td><td>{i['quantity']}</td><td>${i['unit_price']:,.2f}</td><td>${i['unit_price']*i['quantity']:,.2f}</td></tr>"
            for i in items
        )
        ship_label = "Free" if shipping == 0 else f"${shipping:,.2f}"
        addr = f"{customer.get('address','')}, {customer.get('city','')}, {customer.get('state','')} {customer.get('zip','')}"
        if customer.get("country"):
            addr += f", {customer['country']}"
        body = f"""
        <h2>New Order Received</h2>
        <div class="row"><span class="label">Name</span><span class="val">{customer['first_name']} {customer['last_name']}</span></div>
        <div class="row"><span class="label">Phone</span><span class="val">{customer['phone']}</span></div>
        <div class="row"><span class="label">Email</span><span class="val">{customer['email']}</span></div>
        <div class="row"><span class="label">Company</span><span class="val">{customer.get('company','—')}</span></div>
        <div class="row"><span class="label">Delivery</span><span class="val">{addr}</span></div>
        <div class="row"><span class="label">Contact Pref</span><span class="val">{customer.get('contact_pref','—')} / {customer.get('best_time','—')}</span></div>
        <div class="row"><span class="label">Payment</span><span class="val">{customer.get('payment_method','—')}</span></div>
        <table class="items" style="margin-top:16px;">
          <thead><tr><th>Item</th><th>Spec</th><th>Qty</th><th>Unit Price</th><th>Subtotal</th></tr></thead>
          <tbody>{rows}</tbody>
          <tr class="total-row"><td colspan="4">Shipping</td><td>{ship_label}</td></tr>
          <tr class="total-row"><td colspan="4">Total</td><td>${total:,.2f}</td></tr>
        </table>
        <div class="row"><span class="label">Notes</span><span class="val">{customer.get('notes','—')}</span></div>
        <p style="margin-top:24px;"><a href="https://engineswapautos.com/admin" style="background:{ACCENT};color:#fff;padding:10px 20px;text-decoration:none;border-radius:4px;">View in Admin Panel</a></p>
        """
        await _send(OWNER_EMAIL, f"[{BUSINESS_NAME}] New Order — {customer['first_name']} {customer['last_name']} — ${total:,.2f}", _base_html("New Order", body))
    except Exception as e:
        print(f"[email] order owner notification failed: {e}")
