import asyncio
import httpx

async def simulate_user(name: str, token: str, message: str, expected_status: int = 200, expected_region: str = None):
    async with httpx.AsyncClient() as client:
        print(f"[{name}] Sending: '{message}' with Token: {token}...")
        response = await client.post(
            "http://localhost:8000/chat", 
            json={"message": message}, 
            headers={"Authorization": f"Bearer {token}"}
        )
        data = response.json()
        print(f"[{name}] Response: {data}")
        
        # Validation
        if "response" not in data:
            print(f"[{name}] FAILED: No response field")
            return
            
        inner = data["response"]
        
        # Check for expected error vs success
        if "error" in inner:
            if expected_status == 200:
                 print(f"[{name}] FAILED: Expected success but got error: {inner['error']}")
            else:
                 print(f"[{name}] SUCCESS: Got expected error: {inner['error']}")
        else:
            if expected_status != 200:
                print(f"[{name}] FAILED: Expected error but got success: {inner}")
            elif expected_region and inner.get("region") != expected_region:
                print(f"[{name}] FAILED: Expected region {expected_region} but got {inner.get('region')}")
            else:
                print(f"[{name}] SUCCESS: Verified access to {inner.get('region')} as {inner.get('authorized_as')}")

async def main():
    print("--- Starting OBO Verification ---")
    
    # Run tests concurrently to ensure ContextVar isolation works!
    await asyncio.gather(
        # 1. Happy Path User A (US)
        simulate_user("User A", "user_a_token", "Show me US sales", expected_status=200, expected_region="US"),
        
        # 2. Happy Path User B (EU)
        simulate_user("User B", "user_b_token", "Show me EU sales", expected_status=200, expected_region="EU"),
        
        # 3. Unauthorized Access (User A tries EU)
        simulate_user("User A (Malicious)", "user_a_token", "Show me EU sales", expected_status=403),
        
        # 4. Unauthorized Access (User B tries US)
        simulate_user("User B (Lost)", "user_b_token", "Show me US sales", expected_status=403),
    )
    print("--- Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
