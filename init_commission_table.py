#!/usr/bin/env python3
"""
Initialize the commissions table in the database.
This table stores commission calculations for plot sales.
"""

import sqlite3

DB_NAME = 'receipts.db'

def init_commissions_table():
    """Create the commissions table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create commissions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- Input fields (yellow cells from Excel)
            plot_no TEXT,
            sq_yards REAL,
            original_price REAL,
            negotiated_price REAL,
            advance_received REAL,
            agent_commission_rate REAL,
            agreement_percentage REAL,
            amount_paid_at_agreement REAL,
            amc_charges REAL,
            cgm_rate REAL,
            srgm_rate REAL,
            gm_rate REAL,
            agent_rate REAL,
            
            -- Calculated fields
            total_amount REAL,
            w_value REAL,
            b_value REAL,
            balance_amount REAL,
            actual_agreement_amount REAL,
            agreement_balance REAL,
            
            -- Mediator calculations
            mediator_amount REAL,
            mediator_deduction REAL,
            mediator_actual_payment REAL,
            mediator_at_agreement REAL,
            
            -- CGM calculations
            cgm_total REAL,
            cgm_at_agreement REAL,
            cgm_at_registration REAL,
            
            -- SrGM calculations
            srgm_total REAL,
            srgm_at_agreement REAL,
            srgm_at_registration REAL,
            
            -- GM calculations
            gm_total REAL,
            gm_at_agreement REAL,
            gm_at_registration REAL,
            
            -- Agent calculations
            agent_total REAL,
            agent_at_agreement REAL,
            agent_at_registration REAL,
            
            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Commissions table created successfully!")

if __name__ == '__main__':
    init_commissions_table()
