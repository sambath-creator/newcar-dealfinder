import os
import smtplib
from email.message import EmailMessage

def render_email(deals):
    subject = f"Car Deal Finder: {len(deals)} strong deal(s)"
    rows = []
    for d in deals:
        l = d.listing
        reasons = ", ".join(d.reasons) or "meets target criteria"
        rows.append(
            f"<h3>{d.classification} — {l.title} — £{l.price_gbp:,.0f} — score {d.score}/100</h3>"
            f"<p>{l.mileage:,} miles | {l.registration_year} | {l.dealer} | {l.location}</p>"
            f"<p>Distance: {d.distance_miles:.0f} miles | Market discount: {d.discount_pct:.1f}%</p>"
            f"<p>Estimated changeover after PX: £{d.effective_changeover_gbp:,.0f}</p>" if d.effective_changeover_gbp is not None else
            f"<h3>{d.classification} — {l.title} — £{l.price_gbp:,.0f} — score {d.score}/100</h3>"
            f"<p>{l.mileage:,} miles | {l.registration_year} | {l.dealer} | {l.location}</p>"
            f"<p>Distance: {d.distance_miles:.0f} miles | Market discount: {d.discount_pct:.1f}%</p>"
        )
        rows[-1] += f'<p>{reasons}</p><p><a href="{l.url}">View listing</a></p>'
    return subject, "<html><body><h2>New Car Deal Finder</h2>" + "".join(rows) + "</body></html>"

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
