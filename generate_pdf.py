# generate_pdf.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
import os

def format_inr(number):
    try:
        n = int(round(float(number)))
    except Exception:
        return str(number or "")
    s = str(n)
    if len(s) <= 3:
        return s
    last3 = s[-3:]
    rem = s[:-3]
    parts = []
    while len(rem) > 2:
        parts.append(rem[-2:])
        rem = rem[:-2]
    if rem:
        parts.append(rem)
    parts.reverse()
    return ",".join(parts) + "," + last3

def _wrap_lines(c, text, fontname, fontsize, max_width):
    words = str(text or "").split()
    lines = []
    cur = ""
    for w in words:
        cand = (cur + " " + w).strip()
        if c.stringWidth(cand, fontname, fontsize) <= max_width:
            cur = cand
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def get_field(r, *variants, default=""):
    if not isinstance(r, dict):
        return default
    for k in variants:
        if k in r:
            val = r[k]
            if val is not None and str(val).strip() != "":
                return val
    lower_map = {key.lower(): key for key in r.keys()}
    for k in variants:
        kl = k.lower()
        if kl in lower_map:
            val = r[lower_map[kl]]
            if val is not None and str(val).strip() != "":
                return val
    return default

def generate_receipt_pdf_two_copies(r, output_path, template_path=None):
    """
    Two-up receipt generator with smaller label→value gap to avoid large empty spaces.
    """

    PAGE_W, PAGE_H = A4
    c = canvas.Canvas(output_path, pagesize=A4)

    MARGIN = 12 * mm
    GAP = 8 * mm
    PANEL_W = PAGE_W - 2 * MARGIN
    PANEL_H = (PAGE_H - 2 * MARGIN - GAP) / 2.0

    BRAND = colors.HexColor("#f16924")
    MUTED = colors.HexColor("#6b6b6b")
    BLACK = colors.black
    BG = colors.white

    LEFT_X = 15 * mm
    RIGHT_PADDING = 15 * mm
    RIGHT_X = PANEL_W - RIGHT_PADDING

    # Reduced gap between LABEL and VALUE
    VALUE_GAP = 6 * mm   # <<-- reduced gap (was 13mm)

    LOGO_W = 25 * mm
    LOGO_H = 12 * mm

    def field(*names, default=""):
        return get_field(r, *names, default=default)

    def draw_panel(panel_llx, panel_lly, copy_label):
        panel_top = panel_lly + PANEL_H

        # panel bg + border
        c.setFillColor(BG)
        c.roundRect(panel_llx, panel_lly, PANEL_W, PANEL_H, 6, stroke=0, fill=1)
        c.setStrokeColor(MUTED)
        c.setLineWidth(0.8)
        c.roundRect(panel_llx, panel_lly, PANEL_W, PANEL_H, 6, stroke=1, fill=0)

        # logo (center)
        logo_path = os.path.join("static", "images", "logo.png")
        if os.path.exists(logo_path):
            try:
                c.drawImage(
                    logo_path,
                    panel_llx + PANEL_W/2 - LOGO_W/2,
                    panel_top - LOGO_H - 8,
                    LOGO_W, LOGO_H,
                    preserveAspectRatio=True, mask='auto'
                )
            except:
                pass

        # address
        c.setFont("Helvetica", 9); c.setFillColor(MUTED)
        c.drawCentredString(
            panel_llx + PANEL_W/2,
            panel_top - LOGO_H - 16,
            field("address", "Address", default="Opp. Sri Ram Hospitals, Pushpa Hotel Road, Vijayawada")
        )

        # title & copy label
        c.setFont("Helvetica-Bold", 14); c.setFillColor(BRAND)
        c.drawRightString(panel_llx + RIGHT_X, panel_top - LOGO_H - 16, "RECEIPT")
        c.setFont("Helvetica-Bold", 9); c.setFillColor(MUTED)
        c.drawString(panel_llx + LEFT_X, panel_top - LOGO_H - 16, copy_label)

        # starting baseline
        y = panel_top - LOGO_H - 18*mm

        # left: LABEL at y, VALUE at y - VALUE_GAP, then y moves down to next row (y -= VALUE_GAP + small buffer)
        def left(label, value, label_font="Helvetica", label_size=9, value_size=11):
            nonlocal y
            c.setFont(label_font, label_size); c.setFillColor(MUTED)
            c.drawString(panel_llx + LEFT_X, y, label)
            c.setFont("Helvetica-Bold", value_size); c.setFillColor(BLACK)
            c.drawString(panel_llx + LEFT_X, y - VALUE_GAP, str(value or ""))
            y -= (VALUE_GAP + 1*mm)

        def right(label, value, base_y, label_font="Helvetica", label_size=9, value_size=11):
            c.setFont(label_font, label_size); c.setFillColor(MUTED)
            c.drawRightString(panel_llx + RIGHT_X, base_y, label)
            c.setFont("Helvetica-Bold", value_size); c.setFillColor(BLACK)
            c.drawRightString(panel_llx + RIGHT_X, base_y - VALUE_GAP, str(value or ""))

        # robust fields
        no_val = field("no", "No", "receipt_no", "receiptNumber", default="")
        date_val = field("date", "Date", "receipt_date", default="")
        project_val = field("project_name", "project", "Project", default="")
        venture_val = field("venture", "Venture", default="")
        customer_val = field("customer_name", "Customer", "customer", default="")
        payment_mode_val = field("payment_mode", "Payment Mode", "paymentMode", default="")

        amount_formatted_val = field("amount_formatted", "amount_formatted", "amount", "Amount", default="")
        if not amount_formatted_val:
            am_num = field("amount_numeric", "amount_numeric", "amount", default="")
            if am_num not in (None, ""):
                try:
                    amount_formatted_val = format_inr(am_num)
                except:
                    amount_formatted_val = str(am_num)

        plot_no_val = field("plot_no", "plot", "Plot No", default="")
        sqy_val = field("square_yards", "sq_yards", "Sq.Yds", default="")
        purpose_val = field("purpose", "Purpose", default="")
        drawn_bank_val = field("drawn_bank", "drawnBank", "Drawn Bank", default="")
        branch_val = field("branch", "Branch", default="")
        amount_words_val = field("amount_words", "amount_in_words", "Amount (in words)", default="")

        # populate fields using compact spacing
        left("No", no_val)
        right("Date", date_val, y + VALUE_GAP + 1*mm)

        left("Project", project_val)
        right("Venture", venture_val, y + VALUE_GAP + 1*mm)

        # Customer (larger value font)
        c.setFont("Helvetica", 9); c.setFillColor(MUTED)
        c.drawString(panel_llx + LEFT_X, y, "Customer")
        c.setFont("Helvetica-Bold", 12); c.setFillColor(BLACK)
        c.drawString(panel_llx + LEFT_X, y - VALUE_GAP, str(customer_val or ""))
        y -= (VALUE_GAP + 1*mm)

        left("Payment Mode", payment_mode_val)
        right("Amount", "Rs. " + str(amount_formatted_val), y + VALUE_GAP + 1*mm)

        left("Plot No", plot_no_val)
        right("Sq.Yds", sqy_val, y + VALUE_GAP + 1*mm)

        left("Purpose", purpose_val)

        left("Drawn Bank", drawn_bank_val)
        right("Branch", branch_val, y + VALUE_GAP + 1*mm)

        # amount in words (label + wrapped text)
        y_words_label = y - 2*mm
        c.setFont("Helvetica-Bold", 10); c.setFillColor(MUTED)
        c.drawString(panel_llx + LEFT_X, y_words_label, "Amount (in words)")

        text_start_y = y_words_label - 8
        lines = _wrap_lines(c, amount_words_val, "Helvetica-Oblique", 10, PANEL_W - (LEFT_X + RIGHT_PADDING))

        c.setFont("Helvetica-Oblique", 10); c.setFillColor(BLACK)
        yy2 = text_start_y
        for ln in lines[:3]:
            c.drawString(panel_llx + LEFT_X, yy2, ln)
            yy2 -= 10

        # signatures: keep lower and clamped
        desired_sig_y = yy2 - 28 * mm
        min_sig_y = panel_lly + 10 * mm
        max_sig_y = panel_lly + PANEL_H - 12 * mm
        sig_y = max(min(desired_sig_y, max_sig_y), min_sig_y)

        sig_w = 48 * mm
        gap = (PANEL_W - 3 * sig_w) / 4.0
        sx = panel_llx + gap
        for label in ("Cashier", "Accountant", "Authorised Signature"):
            c.setStrokeColor(MUTED)
            c.line(sx, sig_y, sx + sig_w, sig_y)
            c.setFont("Helvetica", 9); c.setFillColor(MUTED)
            c.drawCentredString(sx + sig_w/2.0, sig_y - 10, label)
            sx += sig_w + gap

    # render both copies
    draw_panel(MARGIN, MARGIN, "Customer Copy")
    draw_panel(MARGIN, MARGIN + PANEL_H + GAP, "Office Copy")

    c.showPage()
    c.save()
