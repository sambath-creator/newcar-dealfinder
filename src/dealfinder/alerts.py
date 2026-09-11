import os
import smtplib
from email.message import EmailMessage

def render_email(deals):
    subject = f"🔥 Car Deal Finder: {len(deals)} strong deal(s) found!"
    rows = []
    for d in deals:
        l = d.listing
        reasons = ", ".join(d.reasons) or "meets target criteria"
        img_tag = f'<img src="{l.image_url}" alt="{l.title}" style="width:100%; max-width:400px; border-radius:8px; margin-bottom:10px;">' if l.image_url else ''
        
        badge_color = "#28a745" if d.classification == "BUY" else "#ffc107"
        
        pre_reg_badge = ""
        is_ev = l.model.lower() in ["enyaq", "ev6", "ioniq 5", "e-5008", "enyaq-iv", "ev5", "ix1", "model y", "id.4", "id4", "q4 e-tron", "ariya"]
        if l.mileage < 100 and d.discount_pct > 0 and is_ev:
            pre_reg_badge = f'<span style="background:#6f42c1; color:#fff; padding:4px 8px; border-radius:12px; font-weight:bold; font-size:12px; margin-bottom:5px;">🌟 Pre-Registered</span>'
            
        # Hide NEGOTIATE badge if it's the only badge
        class_badge = ""
        if d.classification != "NEGOTIATE" or pre_reg_badge:
            class_badge = f'<span style="background:{badge_color}; color:#fff; padding:4px 8px; border-radius:12px; font-weight:bold; font-size:12px; margin-bottom:5px;">{d.classification}</span>'
            
        price_section = f"£{l.price_gbp:,.0f}"
        if getattr(d, 'original_list_price_gbp', None) is not None:
            savings = d.original_list_price_gbp - l.price_gbp
            price_section += f' <span style="font-size:0.9em; color:#555;">(Original List Price: £{d.original_list_price_gbp:,.0f} | You save: £{savings:,.0f})</span>'
        elif d.effective_changeover_gbp is not None:
            price_section += f' <span style="font-size:0.9em; color:#555;">(Estimated PX changeover: £{d.effective_changeover_gbp:,.0f})</span>'
            
        dealer_line = ""
        if l.dealer:
            dealer_line = f'<p style="margin:4px 0;"><strong>Dealer:</strong> {l.dealer} ({l.location}, {d.distance_miles:.0f} miles away)</p>'
            
        discount_line = f"<strong>Market Discount:</strong> {d.discount_pct:.1f}% &nbsp;|&nbsp; " if d.discount_pct > 0 else ""
        
        features_str = ", ".join(l.features) if l.features else "Standard Specs"
        
        fuel_str = l.fuel_type.lower()
        if "electric" in fuel_str or "bev" in fuel_str:
            fuel_badge = f'<span style="background:#17a2b8; color:#fff; padding:4px 8px; border-radius:12px; font-weight:bold; font-size:12px; margin-bottom:5px;">⚡ EV</span>'
        elif "plug" in fuel_str or "phev" in fuel_str:
            fuel_badge = f'<span style="background:#28a745; color:#fff; padding:4px 8px; border-radius:12px; font-weight:bold; font-size:12px; margin-bottom:5px;">🔌 PHEV</span>'
        elif "hybrid" in fuel_str or "hev" in fuel_str:
            fuel_badge = f'<span style="background:#85c1e9; color:#fff; padding:4px 8px; border-radius:12px; font-weight:bold; font-size:12px; margin-bottom:5px;">🔋 Hybrid</span>'
        else:
            fuel_badge = f'<span style="background:#6c757d; color:#fff; padding:4px 8px; border-radius:12px; font-weight:bold; font-size:12px; margin-bottom:5px;">⛽ {l.fuel_type.capitalize()}</span>'
        
        rows.append(
            f'<div style="background:#fff; border:1px solid #ddd; border-radius:12px; padding:20px; margin-bottom:20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); font-family: sans-serif; position: relative;">'
            f'<div style="position: absolute; top: 15px; right: 15px; display: flex; flex-direction: column; align-items: flex-end;">'
            f'{class_badge}'
            f'{pre_reg_badge}'
            f'{fuel_badge}'
            f'</div>'
            f'{img_tag}'
            f'<h3 style="margin:0; font-size: 20px; color:#333; width:75%; margin-top:5px; margin-bottom:10px;">{l.title}</h3>'
            f'<h4 style="margin:0 0 10px 0; color:#e0245e; font-size:18px;">{price_section}</h4>'
            f'<div style="color:#666; line-height: 1.5; font-size:14px;">'
            f'<p style="margin:4px 0;"><strong>Score:</strong> {d.score}/100 &nbsp;|&nbsp; <strong>Mileage:</strong> {l.mileage:,} miles &nbsp;|&nbsp; <strong>Year:</strong> {l.registration_year}</p>'
            f'<p style="margin:4px 0;"><strong>Insurance Group:</strong> {l.insurance_group} &nbsp;|&nbsp; <strong>Road Tax:</strong> {l.road_tax}</p>'
            f'<p style="margin:4px 0;"><strong>Key Features:</strong> {features_str}</p>'
            f'{dealer_line}'
            f'<p style="margin:4px 0;">{discount_line}<strong>Reasons:</strong> {reasons}</p>'
            f'</div>'
            f'<div style="margin-top:15px;">'
            f'<a href="{l.url}" style="background:#007bff; color:#fff; text-decoration:none; padding:10px 20px; border-radius:6px; display:inline-block; font-weight:bold;">View Listing</a>'
            f'</div>'
            f'</div>'
        )
        
    html = (
        '<html><body style="background:#f4f7f6; padding:20px;">'
        '<div style="max-width:600px; margin:0 auto; font-family: sans-serif;">'
        '<h2 style="color:#333; text-align:center; margin-bottom:30px;">🚘 Your Latest Car Deals</h2>'
        + "".join(rows) +
        '<p style="text-align:center; color:#999; font-size:12px;">Generated by NewCar DealFinder</p>'
        '</div></body></html>'
    )
    return subject, html

def send_email(deals):
    required = ["SMTP_HOST","SMTP_USERNAME","SMTP_PASSWORD","ALERT_FROM","ALERT_TO"]
    if not all(os.getenv(k) for k in required):
        return False
    subject, html = render_email(deals)
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ["ALERT_FROM"]
    msg["To"] = os.environ["ALERT_TO"]
    msg.set_content("See HTML version.")
    msg.add_alternative(html, subtype="html")
    port = int(os.getenv("SMTP_PORT","587"))
    with smtplib.SMTP(os.environ["SMTP_HOST"], port, timeout=30) as server:
        server.starttls()
        server.login(os.environ["SMTP_USERNAME"], os.environ["SMTP_PASSWORD"])
        server.send_message(msg)
    return True
