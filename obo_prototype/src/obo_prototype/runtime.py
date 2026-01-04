import httpx
from .context import get_current_user_token

class SafeToolExecutor:
    """
    The trusted runtime component. 
    It executes tools but ensures the Outbound Request carries the Inbound Identity.
    """
    
    async def call_sales_db(self, region: str, base_url: str = "http://localhost:8000"):
        """
        A 'Tool' exposed to the LLM. 
        Note: The LLM does NOT match the 'token' argument. 
        The Runtime injects it.
        """
        token = get_current_user_token()
        if not token:
            raise ValueError("Security Error: No active user context found. Cannot execute OBO tool.")
            
        async with httpx.AsyncClient() as client:
            # INJECTION HAPPENS HERE
            # The LLM knows nothing about this header.
            headers = {"Authorization": f"Bearer {token}"}
            
            try:
                response = await client.get(
                    f"{base_url}/mock/sales/data", 
                    params={"region": region},
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                return {"error": f"Access Denied or Error: {e.response.text}"}
            except Exception as e:
                return {"error": str(e)}

# The Agent Logic (simplified)
# In a real app, this would be LangChain or PydanticAI
async def mock_llm_decision_making(prompt: str):
    """
    Simulates an LLM deciding to call a tool.
    Input: "Show me US sales" -> Output: calls call_sales_db("US")
    """
    executor = SafeToolExecutor()
    
    if "US" in prompt:
        return await executor.call_sales_db("US")
    elif "EU" in prompt:
        return await executor.call_sales_db("EU")
    else:
        return {"message": "I don't know which region to query."}
