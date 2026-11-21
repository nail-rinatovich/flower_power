import base64
import binascii


def normalize_render_secret(value):
    """Represent Render's 256-bit Base64 secret as 64 hex characters.

    Preserve the original entropy and keep the result stable across restarts.
    Other values stay unchanged so Django can still reject weak secrets.
    """
    if not value or len(value) >= 50:
        return value
    try:
        decoded = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error):
        return value
    return decoded.hex() if len(decoded) == 32 else value
