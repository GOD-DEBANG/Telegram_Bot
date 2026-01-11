from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import grey, HexColor
from reportlab.lib.units import inch
from datetime import datetime

def generate_ticket_pdf(filename, data):
    """
    data = {
        "ticket_id": str,
        "name": str,
        "email": str,
        "mode": "Flight / Train / Bus",
        "from": str,
        "to": str,
        "seats": list,
        "fare": int,
        "hotel": str or None,
        "hotel_price": int or 0,
        "operator": str
    }
    """
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Custom styles
    styles.add(ParagraphStyle(
        name="Title",
        fontSize=20,
        textColor=HexColor("#1F3C88"),
        spaceAfter=20
    ))

    styles.add(ParagraphStyle(
        name="Section",
        fontSize=14,
        textColor=HexColor("#2E86C1"),
        spaceBefore=12,
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name="NormalRight",
        alignment=2  # TA_RIGHT
    ))

    # HEADER
    elements.append(Paragraph("GoRoute™ Travel Ticket", styles["Title"]))
    elements.append(Paragraph(
        f"Booking Date: {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
        styles["NormalRight"]
    ))
    elements.append(Spacer(1, 12))

    # TICKET INFO
    ticket_table = Table([
        ["Ticket ID", data["ticket_id"]],
        ["Passenger", data["name"]],
        ["Email", data["email"]],
        ["Mode", data["mode"]],
        ["Operator", data["operator"]],
        ["Route", f'{data["from"]} → {data["to"]}'],
        ["Seats", ", ".join(data["seats"])],
        ["Fare", f'₹{data["fare"]}'],
    ], colWidths=[2.2*inch, 3.8*inch])

    ticket_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, grey),
        ("FONT", (0,0), (0,-1), "Helvetica-Bold"),
        ("BACKGROUND", (0,0), (-1,0), HexColor("#F4F6F6")),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6)
    ]))
    elements.append(Paragraph("🎫 Travel Details", styles["Section"]))
    elements.append(ticket_table)
    elements.append(Spacer(1, 12))

    # HOTEL INFO
    if data.get("hotel"):
        hotel_table = Table([
            ["Hotel Name", data["hotel"]],
            ["Hotel Charges", f'₹{data.get("hotel_price",0)} / night']
        ], colWidths=[2.2*inch, 3.8*inch])

        hotel_table.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, grey),
            ("FONT", (0,0), (0,-1), "Helvetica-Bold"),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6)
        ]))

        elements.append(Paragraph("🏨 Hotel Booking", styles["Section"]))
        elements.append(hotel_table)
        elements.append(Spacer(1, 12))

    # PAYMENT SUMMARY
    total_amount = data["fare"] + data.get("hotel_price",0)
    payment_table = Table([
        ["Travel Fare", f'₹{data["fare"]}'],
        ["Hotel Charges", f'₹{data.get("hotel_price",0)}'],
        ["Total Amount", f'₹{total_amount}'],
    ], colWidths=[2.2*inch, 3.8*inch])

    payment_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, grey),
        ("FONT", (0,2), (-1,2), "Helvetica-Bold"),
        ("BACKGROUND", (0,2), (-1,2), HexColor("#E8F6F3")),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6)
    ]))
    elements.append(Paragraph("💳 Payment Summary", styles["Section"]))
    elements.append(payment_table)

    # FOOTER
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "This is a system-generated ticket. Please carry a valid ID during travel.",
        styles["Normal"]
    ))
    elements.append(Paragraph(
        "© GoRoute Technologies Pvt. Ltd.",
        styles["Normal"]
    ))

    doc.build(elements)
