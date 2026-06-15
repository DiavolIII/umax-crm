import re


def validate_phone(phone: str) -> bool:
    cleaned = re.sub(r"[\s\-\(\)\+]", "", phone)
    if cleaned.startswith("8"):
        cleaned = "7" + cleaned[1:]
    if not cleaned.startswith("7") and len(cleaned) == 10:
        cleaned = "7" + cleaned
    return len(cleaned) == 11 and cleaned.isdigit()


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_fio(fio: str) -> bool:
    parts = fio.strip().split()
    if len(parts) < 2:
        return False
    for part in parts:
        if not re.match(r"^[а-яА-ЯёЁa-zA-Z\-]+$", part):
            return False
    return True


def normalize_phone(phone: str) -> str:
    cleaned = re.sub(r"[\s\-\(\)\+]", "", phone)
    if cleaned.startswith("8"):
        cleaned = "7" + cleaned[1:]
    if not cleaned.startswith("7") and len(cleaned) == 10:
        cleaned = "7" + cleaned
    if len(cleaned) == 11 and cleaned[0] == "7":
        return f"+{cleaned}"
    return phone
