import logging
from app.core.config import settings
from itsdangerous import URLSafeTimedSerializer

serializer = URLSafeTimedSerializer(secret_key=settings.JWT_SECRET_KEY, salt="email-verification")

def create_url_safe_token(data : dict):

    token = serializer.dumps(data, salt="email-verification")
    return token


def decode_url_safe_token(token : str):
    try: 
        token_data = serializer.loads(token)

        return token_data
    
    except Exception as e:
        logging.error(str(e))