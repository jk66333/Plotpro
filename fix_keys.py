import re

# Read the file
with open('templates/commission_calculator.html', 'r') as f:
    content = f.read()

# Function to clean up keys
def clean_key(match):
    key = match.group(1).strip()
    return f"commission_data['{key}']"

# Regex to match commission_data[' key ']
# Matches: commission_data['...'] allowing for newlines and spaces
pattern = r"commission_data\['([^']+)'\]"

new_content = re.sub(pattern, clean_key, content)

# Write back
with open('templates/commission_calculator.html', 'w') as f:
    f.write(new_content)

print("Cleaned up whitespace in keys")
