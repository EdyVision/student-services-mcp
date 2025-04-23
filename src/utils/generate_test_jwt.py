import jwt
import time
from datetime import datetime, timedelta


def generate_jwt(secret_key: str = "your-secret-key-here") -> tuple[dict, str]:
    """
    Generate a JWT token with test payload.

    Args:
        secret_key: The secret key to use for signing the JWT

    Returns:
        tuple containing (payload, token)
    """
    # Payload data
    payload = {
        "sub": "TEST_SERVICE1",
        "iat": int(time.time()),  # Current timestamp
        "exp": int(time.time()) + 86400,  # 24 hours from now
        "scope": "read:test1 read:test2",
    }

    # Generate JWT
    token = jwt.encode(payload, secret_key, algorithm="HS256")

    return payload, token


if __name__ == "__main__":
    # When run directly, print the token
    payload, token = generate_jwt()
    print("Payload:")
    print(payload)
    print("\nJWT Token:")
    print(token)
    print("\nTo use in Authorization header:")
    print(f"Authorization: Bearer {token}")
