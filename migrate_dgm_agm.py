"""
Migration script to rename agent fields to DGM and add AGM fields
"""
import database

conn = database.get_db_connection()
c = conn.cursor()

try:
    print("Starting commission table migration...")
    
    # Step 1: Rename agent columns to dgm
    print("1. Renaming agent columns to dgm...")
    c.execute("ALTER TABLE commissions CHANGE COLUMN agent_rate dgm_rate DOUBLE")
    c.execute("ALTER TABLE commissions CHANGE COLUMN agent_name dgm_name VARCHAR(255)")
    c.execute("ALTER TABLE commissions CHANGE COLUMN agent_total dgm_total DOUBLE")
    c.execute("ALTER TABLE commissions CHANGE COLUMN agent_at_agreement dgm_at_agreement DOUBLE")
    c.execute("ALTER TABLE commissions CHANGE COLUMN agent_at_registration dgm_at_registration DOUBLE")
    conn.commit()
    print("✓ Renamed agent columns to dgm")
    
    # Step 2: Add AGM columns
    print("2. Adding AGM columns...")
    c.execute("ALTER TABLE commissions ADD COLUMN agm_rate DOUBLE DEFAULT 0")
    c.execute("ALTER TABLE commissions ADD COLUMN agm_name VARCHAR(255)")
    c.execute("ALTER TABLE commissions ADD COLUMN agm_total DOUBLE DEFAULT 0")
    c.execute("ALTER TABLE commissions ADD COLUMN agm_at_agreement DOUBLE DEFAULT 0")
    c.execute("ALTER TABLE commissions ADD COLUMN agm_at_registration DOUBLE DEFAULT 0")
    conn.commit()
    print("✓ Added AGM columns")
    
    # Step 3: Create commission_dgm_entries table (rename from agent_entries if exists)
    print("3. Creating commission_dgm_entries table...")
    c.execute("""
        CREATE TABLE IF NOT EXISTS commission_dgm_entries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            commission_id INT NOT NULL,
            name VARCHAR(255),
            total_amount DOUBLE,
            at_agreement DOUBLE,
            at_registration DOUBLE,
            FOREIGN KEY (commission_id) REFERENCES commissions(id) ON DELETE CASCADE
        )
    """)
    
    # Check if commission_agent_entries exists and rename it
    c.execute("SHOW TABLES LIKE 'commission_agent_entries'")
    if c.fetchone():
        print("  Migrating data from commission_agent_entries to commission_dgm_entries...")
        c.execute("""
            INSERT INTO commission_dgm_entries (commission_id, name, total_amount, at_agreement, at_registration)
            SELECT commission_id, name, total_amount, at_agreement, at_registration
            FROM commission_agent_entries
        """)
        c.execute("DROP TABLE commission_agent_entries")
        print("  ✓ Migrated and dropped commission_agent_entries")
    
    conn.commit()
    print("✓ Created commission_dgm_entries table")
    
    # Step 4: Create commission_agm_entries table
    print("4. Creating commission_agm_entries table...")
    c.execute("""
        CREATE TABLE IF NOT EXISTS commission_agm_entries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            commission_id INT NOT NULL,
            name VARCHAR(255),
            total_amount DOUBLE,
            at_agreement DOUBLE,
            at_registration DOUBLE,
            FOREIGN KEY (commission_id) REFERENCES commissions(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    print("✓ Created commission_agm_entries table")
    
    print("\n✅ Migration completed successfully!")
    
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    conn.rollback()
finally:
    conn.close()
