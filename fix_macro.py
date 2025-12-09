import re

# Read the file
with open('templates/commission_calculator.html', 'r') as f:
    content = f.read()

# Function to replace val macro calls
def replace_val(match):
    field = match.group(1)
    default = match.group(2) if match.group(2) else "''"
    
    # Handle the default value being a string literal "0"
    if default == '"0"':
        default = "'0'"
    
    return f"{{{{ commission_data['{field}'] if edit_mode else {default} }}}}"

# Regex to match {{ val("field", "default") }} or {{ val("field") }}
# Matches: val("field") or val("field", "default")
pattern = r'\{\{\s*val\("([^"]+)"(?:,\s*([^)]+))?\)\s*\}\}'

new_content = re.sub(pattern, replace_val, content)

# Write back
with open('templates/commission_calculator.html', 'w') as f:
    f.write(new_content)

print("Replaced val macro with direct access")
