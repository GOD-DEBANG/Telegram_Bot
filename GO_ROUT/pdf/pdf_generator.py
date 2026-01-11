from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import qrcode
from io import BytesIO

# ===== PREMIUM COLOR PALETTE =====
COLORS = {
    "primary_dark": HexColor("#0F1C3F"),      # Deep navy
    "primary": HexColor("#1A3A6B"),            # Rich blue
    "primary_light": HexColor("#2E5492"),      # Medium blue
    "accent": HexColor("#4A90E2"),             # Vibrant blue
    "accent_light": HexColor("#6BB6FF"),       # Sky blue
    "gold": HexColor("#FFD700"),               # Gold accent
    "gold_light": HexColor("#FFE44D"),         # Light gold
    "success": HexColor("#27AE60"),            # Green
    "bg_light": HexColor("#F8F9FA"),           # Light background
    "bg_card": HexColor("#FFFFFF"),            # Card background
    "text_dark": HexColor("#2C3E50"),          # Dark text
    "text_muted": HexColor("#7F8C8D"),         # Muted text
    "border": HexColor("#E8ECEF"),             # Light border
    "shadow": HexColor("#BDC3C7"),             # Shadow effect
}

def generate_qr_code(data):
    """Generate QR code with premium styling"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Higher error correction
        box_size=12,  # Larger, clearer QR code
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1A3A6B", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def create_logo():
    """Create a premium GoRoute logo with enhanced styling"""
    from reportlab.graphics.shapes import Drawing, Circle, String, Rect
    from reportlab.graphics import renderPM
    
    d = Drawing(180, 60)
    
    # Outer circle with gradient effect (simulated with multiple circles)
    d.add(Circle(30, 30, 22, fillColor=COLORS["primary"], strokeColor=None))
    d.add(Circle(30, 30, 20, fillColor=COLORS["primary_dark"], strokeColor=None))
    
    # Inner route symbol
    d.add(Circle(30, 30, 12, fillColor=white, strokeColor=None))
    d.add(Circle(30, 30, 4, fillColor=COLORS["accent"], strokeColor=None))
    
    # Premium text with better spacing
    d.add(String(65, 24, "GoRoute", fontSize=26, fillColor=COLORS["primary_dark"], 
                 fontName="Helvetica-Bold"))
    
    buffer = BytesIO()
    img_data = renderPM.drawToString(d, fmt='PNG')
    buffer.write(img_data)
    buffer.seek(0)
    return buffer

def generate_ticket_pdf(filename, data):
    """
    Generate PREMIUM boarding pass style PDF with modern aesthetics
    
    REQUIRED fields:
        "ticket_id": str,
        "name": str,
        "email": str,
        "mode": "Flight / Train / Bus",
        "from": str,
        "to": str,
        "seats": list,
        "fare": int,
        "operator": str
    
    OPTIONAL fields (will be auto-generated if missing):
        "from_code": str (e.g., "DEL"),
        "to_code": str (e.g., "MUM"),
        "hotel": str or None,
        "hotel_price": int or 0,
        "departure_time": str (e.g., "14:30"),
        "arrival_time": str (e.g., "17:45"),
        "gate": str (e.g., "A12"),
        "boarding_time": str (e.g., "14:00")
    """
    
    # Auto-fill missing optional fields
    if "from_code" not in data:
        data["from_code"] = data["from"][:3].upper()
    if "to_code" not in data:
        data["to_code"] = data["to"][:3].upper()
    if "departure_time" not in data:
        data["departure_time"] = "14:30"
    if "arrival_time" not in data:
        data["arrival_time"] = "17:45"
    if "gate" not in data:
        data["gate"] = "—"
    if "boarding_time" not in data:
        data["boarding_time"] = "—"
    
    doc = SimpleDocTemplate(
        filename, 
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=110,  # Increased for premium header
        bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    elements = []
    
    # ===== PREMIUM CUSTOM STYLES =====
    styles.add(ParagraphStyle(
        name="HeaderWhite",
        fontSize=32,  # Larger, bolder header
        textColor=white,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=8,
        leading=36
    ))
    
    styles.add(ParagraphStyle(
        name="SubHeaderWhite",
        fontSize=12,
        textColor=COLORS["accent_light"],
        alignment=TA_CENTER,
        spaceAfter=20,
        leading=14
    ))
    
    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontSize=11,
        textColor=COLORS["text_muted"],
        fontName="Helvetica-Bold",
        spaceBefore=12,
        spaceAfter=6,
        leading=13
    ))
    
    styles.add(ParagraphStyle(
        name="BadgeText",
        fontSize=10,
        textColor=white,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        leading=12
    ))
    
    # Generate QR Code
    qr_data = f"GOROUTE|{data['ticket_id']}|{data['name']}|{data['from']}-{data['to']}|{data['mode']}"
    qr_buffer = generate_qr_code(qr_data)
    qr_img = Image(qr_buffer, width=1.4*inch, height=1.4*inch)
    
    # Create logo
    try:
        logo_buffer = create_logo()
        logo_img = Image(logo_buffer, width=1.8*inch, height=0.6*inch)
    except Exception as e:
        # Enhanced fallback
        logo_img = Paragraph(
            '<b><font size="24" color="#0F1C3F">✈ GoRoute</font></b>', 
            styles["Normal"]
        )
    
    # ===== PREMIUM BOARDING PASS SECTION =====
    elements.append(Spacer(1, -25))
    
    # Logo with premium spacing
    logo_table = Table([[logo_img]], colWidths=[6*inch])
    logo_table.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    elements.append(logo_table)
    elements.append(Spacer(1, 18))
    
    # Premium Ticket Type Badge with GOLD accent
    badge_text = f"✦ ELECTRONIC {data['mode'].upper()} TICKET ✦"
    badge_para = Paragraph(
        f'<para align="center" spaceAfter="0"><font size="11" color="white"><b>{badge_text}</b></font></para>',
        styles["Normal"]
    )
    badge_table = Table([[badge_para]], colWidths=[4.5*inch])
    badge_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), COLORS["gold"]),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LINEABOVE", (0,0), (-1,-1), 2, COLORS["gold_light"]),
        ("LINEBELOW", (0,0), (-1,-1), 2, COLORS["gold_light"]),
    ]))
    elements.append(badge_table)
    elements.append(Spacer(1, 25))
    
    # ===== MAIN ROUTE DISPLAY (EXTRA LARGE, PREMIUM) =====
    route_data = [
        [
            Paragraph(f'<para align="center"><font size="36" color="#1A3A6B"><b>{data["from_code"]}</b></font></para>', styles["Normal"]),
            Paragraph('<para align="center"><font size="28" color="#4A90E2"><b>✈</b></font></para>', styles["Normal"]),
            Paragraph(f'<para align="center"><font size="36" color="#1A3A6B"><b>{data["to_code"]}</b></font></para>', styles["Normal"])
        ],
        [
            Paragraph(f'<para align="center"><font size="10" color="#7F8C8D">{data["from"]}</font></para>', styles["Normal"]),
            Paragraph('', styles["Normal"]),
            Paragraph(f'<para align="center"><font size="10" color="#7F8C8D">{data["to"]}</font></para>', styles["Normal"])
        ]
    ]
    
    route_table = Table(route_data, colWidths=[2*inch, 2*inch, 2*inch])
    route_table.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND", (0,0), (-1,-1), white),
        ("TOPPADDING", (0,0), (-1,-1), 18),
        ("BOTTOMPADDING", (0,0), (-1,-1), 18),
        # Premium double border effect
        ("LINEABOVE", (0,0), (-1,0), 3, COLORS["accent"]),
        ("LINEBELOW", (0,1), (-1,-1), 3, COLORS["accent"]),
    ]))
    elements.append(route_table)
    elements.append(Spacer(1, 25))
    
    # ===== PASSENGER & BOOKING DETAILS (PREMIUM CARD) =====
    detail_data = [
        [
            Paragraph('<font size="9" color="#7F8C8D"><b>PASSENGER NAME</b></font>', styles["Normal"]),
            Paragraph('<font size="9" color="#7F8C8D"><b>BOOKING ID</b></font>', styles["Normal"]),
            Paragraph('<font size="9" color="#7F8C8D"><b>SEAT(S)</b></font>', styles["Normal"])
        ],
        [
            Paragraph(f'<b><font size="13" color="#0F1C3F">{data["name"].upper()}</font></b>', styles["Normal"]),
            Paragraph(f'<b><font size="12" color="#1A3A6B">{data["ticket_id"]}</font></b>', styles["Normal"]),
            Paragraph(f'<b><font size="13" color="#27AE60">{", ".join(data["seats"])}</font></b>', styles["Normal"])
        ]
    ]
    
    detail_table = Table(detail_data, colWidths=[2.3*inch, 2*inch, 1.7*inch])
    detail_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), COLORS["bg_light"]),
        ("LEFTPADDING", (0,0), (-1,-1), 15),
        ("RIGHTPADDING", (0,0), (-1,-1), 15),
        ("TOPPADDING", (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        # Premium triple-line accent
        ("LINEABOVE", (0,0), (-1,0), 4, COLORS["primary"]),
        ("LINEABOVE", (0,0), (-1,0), 1, COLORS["accent"], None, None, 0, 4),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        # Shadow effect
        ("LINEBELOW", (0,1), (-1,-1), 2, COLORS["shadow"]),
    ]))
    elements.append(detail_table)
    elements.append(Spacer(1, 22))
    
    # ===== TIME & GATE INFORMATION (PREMIUM GRID) =====
    time_data = [
        [
            Paragraph('<font size="9" color="#7F8C8D"><b>DEPARTURE</b></font>', styles["Normal"]),
            Paragraph('<font size="9" color="#7F8C8D"><b>ARRIVAL</b></font>', styles["Normal"]),
            Paragraph('<font size="9" color="#7F8C8D"><b>GATE</b></font>', styles["Normal"]),
            Paragraph('<font size="9" color="#7F8C8D"><b>BOARDING</b></font>', styles["Normal"])
        ],
        [
            Paragraph(f'<b><font size="16" color="#1A3A6B">{data["departure_time"]}</font></b>', styles["Normal"]),
            Paragraph(f'<b><font size="16" color="#1A3A6B">{data["arrival_time"]}</font></b>', styles["Normal"]),
            Paragraph(f'<b><font size="16" color="#4A90E2">{data["gate"]}</font></b>', styles["Normal"]),
            Paragraph(f'<b><font size="16" color="#27AE60">{data["boarding_time"]}</font></b>', styles["Normal"])
        ]
    ]
    
    time_table = Table(time_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    time_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), white),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        # Premium grid with accent colors
        ("GRID", (0,0), (-1,-1), 1.5, COLORS["border"]),
        ("LINEABOVE", (0,0), (-1,0), 2, COLORS["accent"]),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    elements.append(time_table)
    elements.append(Spacer(1, 28))
    
    # ===== QR CODE & OPERATOR (PREMIUM FEATURE BOX) =====
    operator_info = [
        Paragraph(f'<font size="9" color="#7F8C8D"><b>OPERATED BY</b></font>', styles["Normal"]),
        Spacer(1, 6),
        Paragraph(f'<b><font size="14" color="#0F1C3F">{data["operator"]}</font></b>', styles["Normal"]),
        Spacer(1, 10),
        Paragraph(f'<font size="9" color="#7F8C8D">📅 {datetime.now().strftime("%d %b %Y, %I:%M %p")}</font>', styles["Normal"]),
        Paragraph(f'<font size="9" color="#4A90E2">📧 {data["email"]}</font>', styles["Normal"])
    ]
    
    qr_section_data = [[qr_img, operator_info]]
    
    qr_table = Table(qr_section_data, colWidths=[1.6*inch, 4.4*inch])
    qr_table.setStyle(TableStyle([
        ("ALIGN", (0,0), (0,0), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 20),
        ("RIGHTPADDING", (0,0), (-1,-1), 20),
        ("BACKGROUND", (0,0), (-1,-1), COLORS["bg_light"]),
        ("TOPPADDING", (0,0), (-1,-1), 18),
        ("BOTTOMPADDING", (0,0), (-1,-1), 18),
        # Premium multi-line border
        ("BOX", (0,0), (-1,-1), 3, COLORS["primary"]),
    ]))
    elements.append(qr_table)
    elements.append(Spacer(1, 30))
    
    # ===== HOTEL SECTION (if applicable) =====
    if data.get("hotel"):
        elements.append(Paragraph("🏨 HOTEL ACCOMMODATION", styles["SectionTitle"]))
        elements.append(Spacer(1, 10))
        
        hotel_data = [
            [
                Paragraph(f'<b><font size="12" color="#0F1C3F">{data["hotel"]}</font></b>', styles["Normal"]),
                Paragraph(f'<b><font size="12" color="#27AE60">₹{data.get("hotel_price", 0)} / night</font></b>', styles["Normal"])
            ]
        ]
        
        hotel_table = Table(hotel_data, colWidths=[4*inch, 2*inch])
        hotel_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), HexColor("#FFF8E1")),
            ("GRID", (0,0), (-1,-1), 1, COLORS["gold"]),
            ("LEFTPADDING", (0,0), (-1,-1), 15),
            ("TOPPADDING", (0,0), (-1,-1), 14),
            ("BOTTOMPADDING", (0,0), (-1,-1), 14),
            ("LINEABOVE", (0,0), (-1,0), 3, COLORS["gold"]),
        ]))
        elements.append(hotel_table)
        elements.append(Spacer(1, 25))
    
    # ===== PAYMENT SUMMARY (PREMIUM TABLE) =====
    elements.append(Paragraph("💳 PAYMENT BREAKDOWN", styles["SectionTitle"]))
    elements.append(Spacer(1, 10))
    
    total_amount = data["fare"] + data.get("hotel_price", 0)
    
    payment_data = [
        [
            Paragraph('<font size="11" color="#2C3E50">Travel Fare</font>', styles["Normal"]),
            Paragraph(f'<font size="11" color="#2C3E50">₹{data["fare"]:,}</font>', styles["Normal"])
        ],
        [
            Paragraph('<font size="11" color="#2C3E50">Hotel Charges</font>', styles["Normal"]),
            Paragraph(f'<font size="11" color="#2C3E50">₹{data.get("hotel_price", 0):,}</font>', styles["Normal"])
        ],
        [
            Paragraph('<b><font size="13" color="white">TOTAL PAID</font></b>', styles["Normal"]),
            Paragraph(f'<b><font size="14" color="white">₹{total_amount:,}</font></b>', styles["Normal"])
        ]
    ]
    
    payment_table = Table(payment_data, colWidths=[4.5*inch, 1.5*inch])
    payment_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,1), white),
        ("BACKGROUND", (0,2), (-1,2), COLORS["primary"]),
        ("GRID", (0,0), (-1,1), 1, COLORS["border"]),
        ("LINEABOVE", (0,2), (-1,2), 4, COLORS["gold"]),
        ("ALIGN", (1,0), (1,-1), "RIGHT"),
        ("LEFTPADDING", (0,0), (-1,-1), 15),
        ("RIGHTPADDING", (0,0), (-1,-1), 15),
        ("TOPPADDING", (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        # Extra emphasis on total
        ("TOPPADDING", (0,2), (-1,2), 15),
        ("BOTTOMPADDING", (0,2), (-1,2), 15),
    ]))
    elements.append(payment_table)
    
    # ===== PREMIUM FOOTER =====
    elements.append(Spacer(1, 35))
    elements.append(Paragraph(
        '<font size="8" color="#95A5A6">⚠ This is a computer-generated ticket. Please carry a valid government-issued photo ID during travel. '
        'Boarding gates close 20 minutes before departure.</font>',
        styles["Normal"]
    ))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        '<font size="8" color="#7F8C8D">© 2026 GoRoute Technologies Pvt. Ltd. | All Rights Reserved | support@goroute.com</font>',
        styles["Normal"]
    ))
    
    # ===== BUILD PDF WITH PREMIUM GRADIENT HEADER =====
    def add_premium_background(canvas, doc):
        canvas.saveState()
        
        # Multi-layer gradient effect (simulated with color bands)
        gradient_colors = [
            (COLORS["primary_dark"], 0),
            (COLORS["primary"], 35),
            (COLORS["primary_light"], 70),
            (COLORS["accent"], 95),
        ]
        
        y_start = A4[1] - 100
        for i, (color, offset) in enumerate(gradient_colors):
            canvas.setFillColor(color)
            canvas.rect(0, y_start + offset, A4[0], 25, fill=True, stroke=False)
        
        # Gold accent stripe at bottom of header
        canvas.setFillColor(COLORS["gold"])
        canvas.rect(0, A4[1] - 105, A4[0], 4, fill=True, stroke=False)
        
        # Decorative corner elements (top corners)
        canvas.setFillColor(COLORS["accent_light"])
        canvas.circle(20, A4[1] - 20, 8, fill=True, stroke=False)
        canvas.circle(A4[0] - 20, A4[1] - 20, 8, fill=True, stroke=False)
        
        canvas.restoreState()
    
    doc.build(elements, onFirstPage=add_premium_background, onLaterPages=add_premium_background)


# Example usage:
if __name__ == "__main__":
    sample_data = {
        "ticket_id": "GR-2026-00123",
        "name": "Rajesh Kumar",
        "email": "rajesh.kumar@email.com",
        "mode": "Flight",
        "from": "New Delhi",
        "to": "Mumbai",
        "from_code": "DEL",
        "to_code": "BOM",
        "seats": ["12A", "12B"],
        "fare": 8500,
        "hotel": "The Grand Plaza Hotel",
        "hotel_price": 3500,
        "operator": "Air India Express",
        "departure_time": "14:30",
        "arrival_time": "16:45",
        "gate": "A12",
        "boarding_time": "14:00"
    }
    
    generate_ticket_pdf("premium_ticket.pdf", sample_data)