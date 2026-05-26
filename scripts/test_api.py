import urllib.request
import json

try:
    req = urllib.request.Request("http://localhost:8080/dashboard/")
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"Status: {resp.status}")
        print(resp.read().decode()[:500])
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(e.read().decode()[:500])
except Exception as e:
    print(f"Error: {e}")
