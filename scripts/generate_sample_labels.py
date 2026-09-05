import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "sample_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def draw_label(filename, header, lines, subheader=None, bg_color="#ffffff", header_color="#1e3a8a"):
    width, height = 750, 480
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Outer border
    draw.rectangle([(15, 15), (width - 15, height - 15)], outline="#1e293b", width=3)

    # Header section
    draw.rectangle([(15, 15), (width - 15, 75)], fill=header_color)
    draw.text((30, 32), header, fill="#ffffff")

    if subheader:
        draw.text((width - 250, 35), subheader, fill="#fef08a")

    # Content lines
    y = 95
    for label, val in lines:
        draw.text((35, y), label, fill="#475569")
        draw.text((260, y), val, fill="#0f172a")
        # subtle divider line
        draw.line([(35, y + 26), (width - 35, y + 26)], fill="#f1f5f9", width=1)
        y += 38

    # Green Veg symbol in bottom right
    veg_x, veg_y = width - 70, height - 70
    draw.rectangle([(veg_x, veg_y), (veg_x + 35, veg_y + 35)], outline="#15803d", width=2)
    draw.ellipse([(veg_x + 7, veg_y + 7), (veg_x + 28, veg_y + 28)], fill="#15803d")

    filepath = os.path.join(OUTPUT_DIR, filename)
    img.save(filepath, "JPEG", quality=95)
    print(f"Created sample label: {filepath}")
    return filepath


# Sample 1: Amul Pasteurized Butter 500g
draw_label(
    filename="amul_butter_500g.jpg",
    header="AMUL PASTEURISED BUTTER",
    subheader="Net Qty: 500 g",
    lines=[
        ("COMMODITY:", "Pasteurised Butter"),
        ("NET QUANTITY:", "500 g"),
        ("MRP (INCL. OF ALL TAXES):", "Rs. 275.00"),
        ("UNIT SALE PRICE:", "Rs. 0.55 / g"),
        ("DATE OF PACKING:", "08/2026"),
        ("BEST BEFORE:", "9 Months from Packing"),
        ("MANUFACTURED BY:", "Kaira District Co-op Milk Producers Union Ltd, Anand - 388001"),
        ("CONSUMER CARE CONTACT:", "1800-258-3333 | customercare@amul.coop"),
    ],
    header_color="#b91c1c" # Amul red
)

# Sample 2: Aashirvaad Shudh Chakki Atta 5kg
draw_label(
    filename="aashirvaad_atta_5kg.jpg",
    header="AASHIRVAAD SHUDH CHAKKI ATTA",
    subheader="100% Whole Wheat",
    lines=[
        ("GENERIC NAME:", "Whole Wheat Flour (Atta)"),
        ("NET QUANTITY:", "5 kg"),
        ("MRP (INCL. OF ALL TAXES):", "Rs. 260.00"),
        ("UNIT SALE PRICE:", "Rs. 52.00 per kg"),
        ("PKD. ON:", "15/08/2026"),
        ("MANUFACTURED & PACKED BY:", "ITC Limited, 37 J.L. Nehru Road, Kolkata - 700071, WB"),
        ("CONSUMER CARE MANAGER:", "Executive, PO Box 592, Bangalore - 560001"),
        ("FEEDBACK / GRIEVANCE:", "Tel: 1800-425-4444 | itccares@itc.in"),
    ],
    header_color="#15803d" # Forest Green
)

# Sample 3: Tata Tea Gold 250g
draw_label(
    filename="tata_tea_gold_250g.jpg",
    header="TATA TEA GOLD - RICH TASTE & AROMA",
    subheader="Premium Blend",
    lines=[
        ("COMMODITY:", "Tea"),
        ("NET QUANTITY:", "250 g"),
        ("MAXIMUM RETAIL PRICE:", "Rs. 165.00 (INCL. OF ALL TAXES)"),
        ("UNIT SALE PRICE:", "Rs. 0.66 / g"),
        ("MONTH & YEAR OF PACKING:", "07/2026"),
        ("MARKETED BY:", "Tata Consumer Products Ltd., 1 Bishop Lefroy Road, Kolkata - 700020"),
        ("COUNTRY OF ORIGIN:", "India"),
        ("CONSUMER CELL:", "1800-345-1720 | care@tataconsumer.com"),
    ],
    header_color="#854d0e" # Tea Golden Brown
)

# Sample 4: Fortune Sunlite Sunflower Oil 1L
draw_label(
    filename="fortune_sunflower_oil_1l.jpg",
    header="FORTUNE SUNLITE SUNFLOWER OIL",
    subheader="Refined Sunflower Oil",
    lines=[
        ("GENERIC NAME:", "Refined Sunflower Oil"),
        ("NET QUANTITY:", "1 L (910 g)"),
        ("MRP (INCLUSIVE OF ALL TAXES):", "Rs. 175.00"),
        ("UNIT SALE PRICE:", "Rs. 175.00 per Litre"),
        ("BATCH NO / MFG DATE:", "BN4410 / 08/2026"),
        ("PRODUCED & PACKED BY:", "Adani Wilmar Limited, Fortune House, Ahmedabad - 380009"),
        ("COUNTRY OF ORIGIN:", "India"),
        ("CUSTOMER CARE TOLL FREE:", "1800-233-9999 | customercare@adaniwilmar.in"),
    ],
    header_color="#0369a1" # Ocean Blue
)

print("All 4 sample packaged commodity labels generated successfully.")
