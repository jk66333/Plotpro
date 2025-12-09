#!/usr/bin/env python3
"""Test the commission PDF generation"""

import sqlite3
from generate_commission_pdf import generate_commission_pdf

# Connect to database and get the first commission record
conn = sqlite3.connect('receipts.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("SELECT * FROM commissions ORDER BY id DESC LIMIT 1")
row = c.fetchone()
conn.close()

if row:
    commission_data = dict(row)
    print(f"Testing PDF generation for commission ID: {commission_data['id']}")
    print(f"Plot No: {commission_data['plot_no']}")
    
    try:
        output_path = f"test_commission_{commission_data['id']}.pdf"
        generate_commission_pdf(commission_data, output_path)
        print(f"✅ PDF generated successfully: {output_path}")
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No commission records found in database")
