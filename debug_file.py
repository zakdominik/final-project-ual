import os
import httpx
from openai import OpenAI

# 1. Check if Heroku actually sees the key
key = os.getenv("OPENAI_KEY")
print(f"--- DEBUG REPORT ---")
if not key:
    print("CRITICAL: OPENAI_KEY is missing/None in environment!")
else:
    print(f"Key found: Yes")
    print(f"Key starts with: {key[:5]}...")
    print(f"Key length: {len(key)} characters")
    # Check for hidden garbage (spaces, newlines)
    if key.strip() != key:
        print("WARNING: Key has hidden spaces or newlines!")

# 2. Test Connection to Google (Basic Internet Check)
print("\nTesting Internet (Google)...")
try:
    httpx.get("https://google.com", timeout=5)
    print("Internet: OK")
except Exception as e:
    print(f"Internet: FAILED ({e})")

# 3. Test OpenAI Connection
print("\nTesting OpenAI Connection...")
try:
    client = OpenAI(api_key=key)
    # Simple call to list models (lightweight)
    client.models.list()
    print("OpenAI Success: Connected and Authorized! ✅")
except Exception as e:
    print(f"OpenAI Failed: ❌")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {e}")
    # If it's a ConnectError, print the underlying cause
    if hasattr(e, '__cause__'):
         print(f"Underlying Cause: {e.__cause__}")

print("--- END REPORT ---")