from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    login = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    role = relationship("Role", back_populates="users")
    applications = relationship("Application", back_populates="manager")
    comments = relationship("ApplicationComment", back_populates="user")

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    applications = relationship("Application", back_populates="source")

class Status(Base):
    __tablename__ = "statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    color_code = Column(String(20), default="#e0e0e0")
    
    applications = relationship("Application", back_populates="status")

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    subject = Column(String(100), nullable=False)
    exam_type = Column(String(20), nullable=False)
    grade = Column(Integer, nullable=False)
    format = Column(String(50), nullable=False)
    price = Column(Integer, nullable=False)
    start_date = Column(Date)
    free_seats = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        CheckConstraint('grade >= 9 AND grade <= 11', name='check_grade'),
        CheckConstraint('price >= 0', name='check_price'),
        CheckConstraint('free_seats >= 0', name='check_free_seats'),
    )
    
    applications = relationship("Application", back_populates="course")

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    application_number = Column(String(20), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    student_full_name = Column(String(200), nullable=False)
    student_grade = Column(Integer, nullable=False)
    parent_full_name = Column(String(200))
    phone = Column(String(20), nullable=False)
    email = Column(String(200))
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    next_contact_date = Column(Date)
    comment = Column(Text)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint('student_grade >= 9 AND student_grade <= 11', name='check_student_grade'),
    )
    
    course = relationship("Course", back_populates="applications")
    source = relationship("Source", back_populates="applications")
    status = relationship("Status", back_populates="applications")
    manager = relationship("User", back_populates="applications")
    comments_history = relationship("ApplicationComment", back_populates="application", cascade="all, delete-orphan")

class ApplicationComment(Base):
    __tablename__ = "application_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    application = relationship("Application", back_populates="comments_history")
    user = relationship("User", back_populates="comments")