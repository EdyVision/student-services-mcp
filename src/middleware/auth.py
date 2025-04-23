from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.settings import settings
import jwt
import time

security = HTTPBearer()

async def verify_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the authentication token."""
    if not settings.auth.AUTH_ENABLED:
        return True

    try:
        # Get the token
        token = credentials.credentials
        
        # Decode the token without verification first to check claims
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        
        # Check if token is older than 1 hour
        current_time = int(time.time())
        if current_time - unverified_payload.get("iat", 0) > 3600:  # 3600 seconds = 1 hour
            # Adjust as needed for your service
            raise HTTPException(
                status_code=401,
                detail="Token is too old (max 1 hour)"
            )
            
        # Check if subject is TEST_SERVICE1 (TODO: Change to Guild JWT Validation)
        if unverified_payload.get("sub") not in ["TEST_SERVICE1", "TEST_SERVICE_2"]:
            raise HTTPException(
                status_code=401,
                detail="Invalid subject"
            )
            
        return True
        
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication error: {str(e)}"
        ) 