from fastapi import APIRouter, Header, HTTPException, Depends

router = APIRouter()

async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    token = authorization.split(" ")[1]
    # In a real app, we'd verify JWT signature here used keys.
    # For prototype, we assume "valid_user_a", "valid_user_b" are valid tokens.
    if token not in ["user_a_token", "user_b_token"]:
        raise HTTPException(status_code=403, detail="Invalid or unauthorized token")
    return token

@router.get("/sales/data")
async def get_sales_data(region: str, token: str = Depends(verify_token)):
    """
    A protected resource.
    If you are 'user_a_token', you can see US data.
    If you are 'user_b_token', you can see EU data.
    """
    # Simple RBAC/Row-Level Logic
    if token == "user_a_token":
        if region == "US":
            return {"data": ["Sales A1", "Sales A2"], "region": "US", "authorized_as": "User A"}
        else:
            raise HTTPException(status_code=403, detail="User A is not authorized for this region")
    
    if token == "user_b_token":
        if region == "EU":
            return {"data": ["Sales B1", "Sales B2"], "region": "EU", "authorized_as": "User B"}
        else:
            raise HTTPException(status_code=403, detail="User B is not authorized for this region")
            
    return {"error": "Unexpected state"}
