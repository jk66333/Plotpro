import database
from flask import Flask, render_template, request, redirect, url_for, send_file, abort
from datetime import datetime
import io
import os

# Optional PDF export
try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except Exception:
    PDFKIT_AVAILABLE = False

DB_PATH = "receipts.db"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'


def init_db():
    conn = database.get_db_connection()
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS receipts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        no VARCHAR(255),
        project_name VARCHAR(255),
        date VARCHAR(255),
        venture VARCHAR(255),
        customer_name VARCHAR(255),
        amount_numeric DOUBLE,
        amount_words TEXT,
        plot_no VARCHAR(255),
        square_yards VARCHAR(255),
        purpose TEXT,
        drawn_bank VARCHAR(255),
        branch VARCHAR(255),
        payment_mode VARCHAR(255),
        created_at VARCHAR(255)
    );
    ''')
    conn.commit()
    conn.close()


def format_inr(number):
    """Format number in Indian style like 1,33,31,250
       Accepts int or float or numeric string. Returns string.
    """
    try:
        n = int(round(float(number)))
    except Exception:
        return number
    s = str(n)
    # last 3 digits
    if len(s) <= 3:
        return s
    else:
        last3 = s[-3:]
        rem = s[:-3]
        parts = []
        while len(rem) > 2:
            parts.append(rem[-2:])
            rem = rem[:-2]
        if rem:
            parts.append(rem)
        parts.reverse()
        return ','.join(parts) + ',' + last3


def number_to_words(n):
    # Simple English converter for demo only — you may replace with a library
    # This function returns a simple words string for whole rupees only.
    # For production use, use `num2words` library with lang='en_IN' if needed.
    try:
        import math
        from num2words import num2words
        return num2words(int(math.floor(float(n))), to='cardinal', lang='en_IN').replace('-', ' ').title()
    except Exception:
        # fallback: just return numeric value followed by "Only"
        return f"{format_inr(n)} Only"


@app.route("/")
def index():
    # form to create a receipt
    conn = database.get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, no, customer_name, date FROM receipts ORDER BY id DESC LIMIT 10")
    rows = database.fetch_all(c)
    conn.close()
    return render_template("form.html", recent=rows)


@app.route("/create", methods=["POST"])
def create():
    form = request.form
    no = form.get("no", "").strip()
    project_name = form.get("project_name", "")
    date = form.get("date", "")
    venture = form.get("venture", "")
    customer_name = form.get("customer_name", "")
    amount_numeric = form.get("amount_numeric", "0").replace(',', '').strip()
    amount_words = form.get("amount_words", "").strip() or number_to_words(amount_numeric)
    plot_no = form.get("plot_no", "")
    square_yards = form.get("square_yards", "")
    purpose = form.get("purpose", "")
    drawn_bank = form.get("drawn_bank", "")
    branch = form.get("branch", "")
    payment_mode = form.get("payment_mode", "")

    created_at = datetime.utcnow().isoformat()

    conn = database.get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO receipts
        (no, project_name, date, venture, customer_name, amount_numeric, amount_words,
         plot_no, square_yards, purpose, drawn_bank, branch, payment_mode, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (no, project_name, date, venture, customer_name, amount_numeric, amount_words,
          plot_no, square_yards, purpose, drawn_bank, branch, payment_mode, created_at))
    conn.commit()
    rid = c.lastrowid
    conn.close()
    return redirect(url_for('view_receipt', receipt_id=rid))


@app.route("/receipt/<int:receipt_id>")
def view_receipt(receipt_id):
    conn = database.get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM receipts WHERE id = %s", (receipt_id,))
    row = database.fetch_one(c)
    conn.close()
    if not row:
        abort(404)
    r = dict(row)
    r['amount_formatted'] = format_inr(r['amount_numeric'])
    return render_template("receipt.html", r=r)


@app.route("/receipt/<int:receipt_id>/pdf")
def receipt_pdf(receipt_id):
    # Optional PDF generation (requires pdfkit + wkhtmltopdf installed)
    if not PDFKIT_AVAILABLE:
        return "PDF export is not available (pdfkit not installed). Use browser print instead.", 400
    receipt_url = url_for('view_receipt', receipt_id=receipt_id, _external=True)
    # create PDF from the rendered URL
    try:
        pdf = pdfkit.from_url(receipt_url, False)
        return send_file(io.BytesIO(pdf), mimetype="application/pdf",
                         download_name=f"receipt_{receipt_id}.pdf")
    except Exception as e:
        return f"PDF generation error: {e}", 500


if __name__ == "__main__":
    init_db()
    # make sure static images folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, port=5000)

