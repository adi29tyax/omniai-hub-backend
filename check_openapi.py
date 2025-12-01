import httpx
import sys
import json

BASE_URL = "http://127.0.0.1:8002"

def check_openapi():
    try:
        r = httpx.get(f"{BASE_URL}/openapi.json")
        if r.status_code == 200:
            data = r.json()
            security_schemes = data.get("components", {}).get("securitySchemes", {})
            print("Security Schemes:", json.dumps(security_schemes, indent=2))
            
            security = data.get("security", [])
            print("Global Security:", json.dumps(security, indent=2))
            
            if "BearerAuth" in security_schemes and security_schemes["BearerAuth"]["type"] == "http":
                print("SUCCESS: BearerAuth found.")
            else:
                print("FAILURE: BearerAuth not found or incorrect.")
        else:
            print(f"Failed to get openapi.json: {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_openapi()
