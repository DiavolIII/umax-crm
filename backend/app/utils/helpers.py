from sqlalchemy.orm import Session
from app.models import Application

def generate_application_number(db: Session) -> str:
    last_app = db.query(Application).order_by(Application.id.desc()).first()
    if last_app and last_app.application_number and last_app.application_number.startswith('Z'):
        try:
            last_num = int(last_app.application_number[1:])
            new_num = last_num + 1
        except:
            new_num = 1001
    else:
        new_num = 1001
    
    return f"Z{new_num:06d}"