import urllib.request
import urllib.parse
import http.cookiejar
import sys

# Setup cookie jar
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Login
login_url = "http://127.0.0.1:5000/login"
login_data = urllib.parse.urlencode({"username": "admin", "password": "password123"}).encode()

print("Logging in...")
try:
    opener.open(login_url, data=login_data)
except Exception as e:
    print(f"Login failed: {e}")
    sys.exit(1)

# Get PDF
pdf_url = "http://127.0.0.1:5000/commission_pdf/1"
print(f"Fetching PDF from {pdf_url}...")

try:
    response = opener.open(pdf_url)
    print(f"Status Code: {response.getcode()}")
    print("Headers:")
    for k, v in response.headers.items():
        print(f"  {k}: {v}")
        
    content = response.read()
    print(f"Content Length: {len(content)} bytes")
    if len(content) > 0:
        print(f"First 20 bytes: {content[:20]}")
    else:
        print("Content is empty!")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} {e.reason}")
    print(e.read())
except Exception as e:
    print(f"Error: {e}")
