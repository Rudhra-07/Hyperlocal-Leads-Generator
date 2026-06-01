import re

def is_valid_email(email: str) -> bool:
    """Simple regex for email validation."""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone: str) -> bool:
    """Simple regex for phone validation (broad)."""
    if not phone:
        return False
    # Matches various formats: +44 123 456 7890, 020 1234 5678, etc.
    pattern = r'^(\+?\d{1,4}[\s-]?)?(\(?\d{3}\)?[\s-]?)?[\d\s-]{7,15}$'
    return re.match(pattern, phone.strip()) is not None
