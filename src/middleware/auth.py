from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.settings import settings
import jwt
import time
import re
import requests

security = HTTPBearer()


def is_jwt_token(token: str) -> bool:
    """Check if the token is a JWT by looking for the typical JWT pattern."""
    # JWT pattern: three base64url-encoded segments separated by dots
    jwt_pattern = r"^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*$"
    return bool(re.match(jwt_pattern, token))


async def validate_huggingface_token(token: str) -> bool:
    """Validate a HuggingFace token by making a request to their API."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("https://huggingface.co/api/whoami-v2", headers=headers)
        return response.status_code == 200
    except Exception:
        return False


async def verify_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the authentication token, supporting both JWT and HuggingFace tokens."""
    if not settings.auth.AUTH_ENABLED:
        return True

    try:
        # Get the token
        token = credentials.credentials

        # Check if it's a JWT token
        if is_jwt_token(token):
            # Decode the token without verification first to check claims
            unverified_payload = jwt.decode(token, options={"verify_signature": False})

            # Check if token is older than 1 hour
            current_time = int(time.time())
            if (
                current_time - unverified_payload.get("iat", 0) > 3600
            ):  # 3600 seconds = 1 hour
                raise HTTPException(
                    status_code=401, detail="Token is too old (max 1 hour)"
                )

            # Check if subject is TEST_SERVICE1 (TODO: Change to Guild JWT Validation)
            if unverified_payload.get("sub") not in ["TEST_SERVICE1", "TEST_SERVICE_2"]:
                raise HTTPException(status_code=401, detail="Invalid subject")
        else:
            # For non-JWT tokens, try to validate as a HuggingFace token
            if not await validate_huggingface_token(token):
                raise HTTPException(status_code=401, detail="Invalid HuggingFace token")

        return True

    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")
