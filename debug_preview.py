
from flask import Flask, render_template, url_for, g
import os
import sys
import json

# Mock database
class MockDB:
    def get_db_connection(self):
        return self
    def cursor(self):
        return self
    def execute(self, query, params):
        self.last_query = query
        self.last_params = params
    def fetchone(self):
        # Full mock row with all fields expected by raw_commission_pdf
        return {
            "plot_no": "123", 
            "sq_yards": 200, 
            "original_price": 5000, 
            "negotiated_price": 4500,
            "advance_received": 100000,
            "agreement_percentage": 0.25,
            "amount_paid_at_agreement": 50000,
            "amc_charges": 0,
            "cgm_rate": 100, "cgm_name": "CGM1",
            "srgm_rate": 50, "srgm_name": "SRGM1",
            "gm_rate": 20, "gm_name": "GM1",
            "dgm_rate": 10, "dgm_name": "DGM1",
            "agm_rate": 5, "agm_name": "AGM1",
            "agent_rate": 2300, "agent_name": "Broker1",
            "total_amount": 900000,
            "w_value": 0, "b_value": 0, "balance_amount": 0,
            "actual_agreement_amount": 0, "agreement_balance": 0,
            "cgm_total": 0, "cgm_at_agreement": 0, "cgm_at_registration": 0,
            "srgm_total": 0, "srgm_at_agreement": 0, "srgm_at_registration": 0,
            "gm_total": 0, "gm_at_agreement": 0, "gm_at_registration": 0,
            "dgm_total": 0, "dgm_at_agreement": 0, "dgm_at_registration": 0,
            "agm_total": 0, "agm_at_agreement": 0, "agm_at_registration": 0,
            "commission_breakdown": None,
            "broker_commission": 2300
        }
    def close(self):
        pass

import database
database.get_db_connection = lambda: MockDB()
database.fetch_one = lambda c: c.fetchone()

# Import app
sys.path.append(os.getcwd())
try:
    from receipt_app import app, generate_commission_pdf_bytes, raw_commission_pdf
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

# Running Test
print("Testing generate_commission_pdf_bytes...")
try:
    # Construct Mock Data
    row = MockDB().fetchone()
    form_data = {
        'plot_no': row['plot_no'],
        'sq_yards': row['sq_yards'],
        'original_price': row['original_price'],
        'negotiated_price': row['negotiated_price'],
        'advance_received': row["advance_received"],
        'agreement_percentage': row["agreement_percentage"],
        'amount_paid_at_agreement': row["amount_paid_at_agreement"],
        'amc_charges': row["amc_charges"],
        'cgm_rate': row['cgm_rate'], 'cgm_name': row['cgm_name'],
        'srgm_entries': [('SRGM1', 50)],
        'gm_entries': [('GM1', 20)],
        'dgm_entries': [('DGM1', 10)],
        'agm_entries': [('AGM1', 5)],
        'broker_commission': row['broker_commission']
    }
    calcs = {k:v for k,v in row.items() if k not in form_data} # sloppy but fine for test
    
    pdf = generate_commission_pdf_bytes(form_data, calcs)
    print(f"Success! PDF size: {len(pdf.getvalue())} bytes")
except Exception as e:
    print("CRASHED inside generate_commission_pdf_bytes:")
    import traceback
    traceback.print_exc()

print("Testing raw_commission_pdf(62, 'test.pdf')...")
try:
    with app.test_request_context():
        resp = raw_commission_pdf(62, "test.pdf")
        print("Success Route!")
except Exception as e:
    print("CRASHED inside raw_commission_pdf:")
    import traceback
    traceback.print_exc()
