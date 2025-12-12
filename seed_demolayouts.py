
import mysql.connector
import os
from dotenv import load_dotenv
import datetime
import random

load_dotenv()

def seed_data():
    print("Seeding Demolayouts Data...")
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database="plotpro_demolayouts"
        )
        c = conn.cursor(dictionary=True)

        # ---------------------------------------------------------
        # 1. Clear existing data
        # ---------------------------------------------------------
        print("Cleaning up old data...")
        c.execute("DELETE FROM commission_agent_entries") # Just in case
        c.execute("DELETE FROM commissions") # Cascades to all entries tables
        c.execute("DELETE FROM receipts")
        c.execute("DELETE FROM projects")
        
        # ---------------------------------------------------------
        # 2. Insert Projects
        # ---------------------------------------------------------
        projects = [
            ("Sunflower Gardens", 150, 20),
            ("Green Valley", 60, 5),
            ("Harmony Heights", 40, 0)
        ]
        c.executemany("INSERT INTO projects (name, total_plots, plots_to_landowners) VALUES (%s, %s, %s)", projects)
        print(f"✅ Added {len(projects)} Projects")
        
        # ---------------------------------------------------------
        # 3. Create Receipts (Simulate Sold Plots)
        # ---------------------------------------------------------
        receipt_data = []
        payment_modes = ["CASH", "Online Transfer", "Cheque"]
        
        for i in range(1, 46): # 45 Receipts
            basic_price = random.randint(15000, 25000)
            sq_yards = random.randint(180, 250)
            payment_mode = random.choice(payment_modes)
            project = "Sunflower Gardens" if i <= 25 else "Green Valley"
            plot_no = str(i)
            
            # Store for receipt insertion
            receipt_data.append((
                f"REC-{i:03d}",
                f"Customer {i}",
                project,
                plot_no,
                120000, # amount_numeric (generic placeholder or part payment)
                datetime.date.today() - datetime.timedelta(days=i),
                str(basic_price),
                str(sq_yards),
                payment_mode
            ))

        c.executemany("""
            INSERT INTO receipts (no, customer_name, project_name, plot_no, amount_numeric, date, basic_price, square_yards, payment_mode) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, receipt_data)
        print(f"✅ Added {len(receipt_data)} Receipts")
        conn.commit()

        # ---------------------------------------------------------
        # 4. Generate Commissions for these Receipts
        # ---------------------------------------------------------
        print("Generating Commission Data...")
        
        # Fetch the receipts we just inserted to ensure consistency
        c.execute("SELECT plot_no, project_name, basic_price, square_yards FROM receipts")
        receipts_fetched = c.fetchall()
        
        for r in receipts_fetched:
            # Parse data
            try:
                plot_no = r['plot_no']
                project_name = r['project_name']
                basic_price = float(r['basic_price'])
                sq_yards = float(r['square_yards'])
            except:
                continue # Skip if bad data

            # --- Financials ---
            original_price = basic_price
            # Negotiated Price >= 700. Let's make it slightly less than original (discount)
            discount = random.randint(0, 1000)
            negotiated_price = max(700, original_price - discount)
            
            total_amount = sq_yards * negotiated_price
            advance_received = 200000
            agreement_percentage = 25.0
            amount_paid_at_agreement = total_amount * 0.25
            amc_charges = 0 # Requested by user
            
            balance_amount = total_amount - amount_paid_at_agreement # Simplified logic
            
            # --- Commission Rates (Constraints) ---
            # CGM <= 500
            cgm_rate = random.randint(100, 500)
            # GM <= 200
            gm_rate = random.randint(50, 200)
            # DGM <= 200
            dgm_rate = random.randint(50, 200)
            # AGM <= 1400
            agm_rate = random.randint(500, 1400)
            # Broker (Agent) = 2300 Default
            agent_rate = 2300
            # SRGM (Not specified, pick reasonable)
            srgm_rate = random.randint(50, 300)

            # --- Calculate Totals ---
            cgm_total = cgm_rate * sq_yards
            srgm_total = srgm_rate * sq_yards
            gm_total = gm_rate * sq_yards
            dgm_total = dgm_rate * sq_yards
            agm_total = agm_rate * sq_yards
            agent_total = agent_rate * sq_yards
            
            # --- Generate Names (Single strings for Main Table) ---
            # Usually strict single mapping for this seed data
            cgm_name = f"CGM User {random.randint(1,2)}"
            srgm_name = "SRGM User 1"
            gm_name = f"GM User {random.randint(1,2)}"
            dgm_name = f"DGM User {random.randint(1,3)}"
            agm_name = f"AGM User {random.randint(1,5)}"
            agent_name = f"Broker {plot_no}"

            # --- Insert Parent Commission (With ALL Names + AMC Charges) ---
            c.execute("""
                INSERT INTO commissions (
                    plot_no, project_name, sq_yards, 
                    original_price, negotiated_price, 
                    advance_received, agreement_percentage, amount_paid_at_agreement, total_amount, balance_amount,
                    amc_charges,
                    cgm_rate, srgm_rate, gm_rate, dgm_rate, agm_rate, agent_commission_rate,
                    cgm_total, srgm_total, gm_total, dgm_total, agm_total, agent_total,
                    broker_commission, cgm_name, srgm_name, gm_name, dgm_name, agm_name
                ) VALUES (
                    %s, %s, %s,
                    %s, %s,
                    %s, %s, %s, %s, %s,
                    %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
            """, (
                plot_no, project_name, sq_yards,
                original_price, negotiated_price,
                advance_received, agreement_percentage, amount_paid_at_agreement, total_amount, balance_amount,
                amc_charges,
                cgm_rate, srgm_rate, gm_rate, dgm_rate, agm_rate, agent_rate,
                cgm_total, srgm_total, gm_total, dgm_total, agm_total, agent_total,
                agent_total, cgm_name, srgm_name, gm_name, dgm_name, agm_name
            ))
            
            commission_id = c.lastrowid

            # --- Insert Entries (Child Tables for Multi-Entry Roles) ---
            # Using the SAME names as generated above
            
            # 1. Agent
            c.execute("INSERT INTO commission_agent_entries (commission_id, name, total_amount) VALUES (%s, %s, %s)", 
                      (commission_id, agent_name, agent_total))
            
            # 2. AGM
            c.execute("INSERT INTO commission_agm_entries (commission_id, name, total_amount) VALUES (%s, %s, %s)", 
                      (commission_id, agm_name, agm_total))
            
            # 3. DGM
            c.execute("INSERT INTO commission_dgm_entries (commission_id, name, total_amount) VALUES (%s, %s, %s)", 
                      (commission_id, dgm_name, dgm_total))
            
            # 4. GM
            c.execute("INSERT INTO commission_gm_entries (commission_id, name, total_amount) VALUES (%s, %s, %s)", 
                      (commission_id, gm_name, gm_total))
            
            # 5. SRGM
            c.execute("INSERT INTO commission_srgm_entries (commission_id, name, total_amount) VALUES (%s, %s, %s)", 
                      (commission_id, srgm_name, srgm_total))

        print(f"✅ Generated Commissions for {len(receipts_fetched)} plots")
        
        conn.commit()
        conn.close()
        print("✅ Seeding Complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    seed_data()
