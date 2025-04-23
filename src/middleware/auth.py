from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.settings import settings

security = HTTPBearer()

async def verify_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the authentication token."""
    if not settings.auth.AUTH_ENABLED:
        return True

    print(f"Received JWT: {credentials.credentials}")
    # TODO: Implement JWT validation
    return True 