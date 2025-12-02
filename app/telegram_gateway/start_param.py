"""
Telegram Gateway - Start Param Security
HMAC-based start parameter verification
"""
import hmac
import hashlib
import json
import time
from typing import Optional

from app.core.config import settings


def generate_start_param(
    telegram_user_id: int,
    user_hint: Optional[str] = None,
    nonce: Optional[str] = None,
) -> str:
    """
    Start parameter oluştur (HMAC signed).
    
    Format: base64({user_hint, ts, nonce, telegram_user_id}) + HMAC
    
    Returns:
        Signed start parameter string
    """
    secret = getattr(settings, "TELEGRAM_LINK_SECRET", None) or settings.JWT_SECRET
    
    ts = int(time.time())
    nonce = nonce or hashlib.sha256(f"{telegram_user_id}{ts}".encode()).hexdigest()[:16]
    
    payload = {
        "telegram_user_id": telegram_user_id,
        "user_hint": user_hint,
        "ts": ts,
        "nonce": nonce,
    }
    
    payload_json = json.dumps(payload, sort_keys=True)
    payload_b64 = payload_json.encode('utf-8')
    
    # HMAC signature
    signature = hmac.new(
        secret.encode('utf-8'),
        payload_b64,
        hashlib.sha256
    ).hexdigest()
    
    # Return: payload.signature
    return f"{payload_json}.{signature}"


def verify_start_param(start_param: str) -> tuple[bool, Optional[dict]]:
    """
    Start parameter doğrula.
    
    Returns:
        (is_valid, payload_dict)
    """
    if not start_param:
        return False, None
    
    try:
        # Split payload and signature
        if '.' not in start_param:
            return False, None
        
        payload_json, signature = start_param.rsplit('.', 1)
        
        secret = getattr(settings, "TELEGRAM_LINK_SECRET", None) or settings.JWT_SECRET
        
        # Verify HMAC
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return False, None
        
        # Parse payload
        payload = json.loads(payload_json)
        
        # Check timestamp (max 1 hour old)
        ts = payload.get("ts", 0)
        if time.time() - ts > 3600:
            return False, None
        
        return True, payload
        
    except Exception:
        return False, None

