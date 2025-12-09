import re

def convert_file(filename):
    print(f"Converting {filename}...")
    with open(filename, 'r') as f:
        content = f.read()

    # Replace ? with %s
    content = content.replace('?', '%s')

    # Replace imports
    content = content.replace('import sqlite3', 'import database')
    
    # Replace connection
    content = content.replace('conn = sqlite3.connect(DB_PATH)', 'conn = database.get_db_connection()')
    
    # Remove row_factory
    content = re.sub(r'conn\.row_factory = sqlite3\.Row\n', '', content)
    content = re.sub(r'conn\.row_factory = sqlite3\.Row', '', content)

    # Replace fetchone/fetchall
    content = re.sub(r'(\w+)\.fetchone\(\)', r'database.fetch_one(\1)', content)
    content = re.sub(r'(\w+)\.fetchall\(\)', r'database.fetch_all(\1)', content)
    
    # Fix broken comment
    content = content.replace('Respects optional %sproject=<name>', 'Respects optional ?project=<name>')
    
    # Fix regex sub that might have been broken if it contained ? (it didn't, but good to check)
    # The regex was r'[^A-Za-z0-9._-]+' which has no ?
    
    with open(filename, 'w') as f:
        f.write(content)
    print(f"Converted {filename}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            convert_file(filename)
    else:
        print("Usage: python convert_code.py <filename>")
