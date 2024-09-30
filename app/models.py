from typing import Optional
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import sqlalchemy as sa
import sqlalchemy.orm as so
from datetime import datetime, timedelta
import random


@login.user_loader
def load_user(id):
    # Load a user by ID for Flask-Login
    return db.session.get(User, int(id))


class User(db.Model, UserMixin):
    "Represents a user in the system with authentication capabilities."
    
    __tablename__ = 'users'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)  # Primary key
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)  # Unique username with index
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(256), unique=True)  # Hashed password

    def __repr__(self):
        return '<User {}>'.format(self.username)  # User representation

    def set_password(self, password):
        # Set hashed password
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # Verify password against hash
        return check_password_hash(self.password_hash, password)


class BaseModel():
    "Base model class providing common attributes for all models."
    
    __abstract__ = True  # Mark this class as abstract
    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)  # Primary key with auto-increment
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, default=datetime.utcnow)  # Timestamp when the record was created
    updated_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Timestamp when the record was last updated



class Student(db.Model, BaseModel):
    "Represents a student in the system."
    
    __tablename__ = 'students'
    student_id: so.Mapped[str] = so.mapped_column(
        sa.String(20), unique=True, nullable=False)  # Unique student ID
    fullname: so.Mapped[str] = so.mapped_column(sa.String(25), nullable=False) # Student's full name
    gender: so.Mapped[str] = so.mapped_column(sa.String(10), nullable=False)  # Student's gender
    year: so.Mapped[str] = so.mapped_column(sa.String(25), nullable=False)  # Year of study
    department: so.Mapped[str] = so.mapped_column(sa.String(25), nullable=False)  # Department
    profile_img: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)  # Path to profile image
    total_library_time: so.Mapped[sa.types.Interval] = so.mapped_column(
        sa.types.Interval(), default=timedelta(seconds=0), nullable=False) # Total library time

    laptop_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('laptops.id', ondelete='CASCADE'), nullable=True) # Foreign key to Laptop table

    
    laptop: so.Mapped['Laptop'] = so.relationship(
        'Laptop', back_populates='student') # Relationship with Laptop model

    lib_logs: so.Mapped['LibLogs'] = so.relationship(
        'LibLogs',
        back_populates='student',
        cascade = 'all, delete-orphan',
        collection_class=list) # Relationship with LibLogs model

    exit_logs: so.Mapped['ExitLogs'] = so.relationship(
        'ExitLogs',
        back_populates='student',
        cascade = 'all, delete-orphan',
        collection_class=list) # Relationship with ExitLogs model

    def __repr__(self):
        return f'<Student {self.fullname}>'  # String representation of the Student object


class LaptopImage(db.Model):
    "Represents an image associated with a laptop."
    
    __tablename__ = 'laptop_images'
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)  # Primary key
    laptop_in_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('laptops.id'), nullable=False) # Foreign key to Laptop table
    image_path: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)  # Path to the laptop image

    laptop: so.Mapped['Laptop'] = so.relationship('Laptop', back_populates='images')  # Relationship with Laptop model


class Laptop(db.Model, BaseModel):
    "Represents a laptop assigned to a student."
    
    __tablename__ = 'laptops'
    laptop_unique_id: so.Mapped[int] = so.mapped_column(
        sa.Integer, unique=True, nullable=False) # Unique identifier for the laptop

    images: so.Mapped['LaptopImage'] = so.relationship(
        'LaptopImage',
        back_populates='laptop',
        cascade='all, delete-orphan',
        collection_class=list)  # Relationship with LaptopImage model
    student: so.Mapped['Student'] = so.relationship(
        'Student',
        back_populates='laptop',
        uselist=False,
        cascade='all, delete-orphan')  # Relationship with Student model

    def __init__(self):
        self.laptop_unique_id = self.generate_unique_laptop_id() # Initialize unique laptop ID

    def add_laptop_image(self, image_path):
        # Add a new laptop image
        new_image = LaptopImage(image_path=image_path, laptop=self)
        self.images.append(new_image)
        db.session.add(new_image)

    @staticmethod
    def generate_unique_laptop_id():
        # Generate a unique 5-digit laptop ID
        while 1:
            laptop_id = random.randint(10000, 99999)
            is_laptop_id_exist = db.session.scalar(
                sa.select(Laptop).where(
                    Laptop.laptop_unique_id == laptop_id))
            if not is_laptop_id_exist:
                break
        return laptop_id

    def __repr__(self):
        return f'<Laptop {self.laptop_unique_id}>'  # String representation of the Laptop object


class LibLogs(db.Model):
    "Represents a log entry for a student's library activities."
    
    __tablename__ = 'lib_logs'
    id: so.Mapped['int'] = so.mapped_column(sa.Integer, primary_key=True) # Primary key
    student_id: so.Mapped[str] = so.mapped_column(
        sa.ForeignKey('students.student_id', ondelete='CASCADE'),
        nullable=False) # Foreign key linking to the Student table
    timestamp: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, default=datetime.utcnow)  # Timestamp of the log entry
    status: so.Mapped[str] = so.mapped_column(
        sa.String(20), nullable=False, default='OUT')  # Status, default is 'OUT'

    student: so.Mapped[Student] = so.relationship(
        'Student',
        back_populates='lib_logs') # Relationship to the Student model


class ExitLogs(db.Model):
    "Represents a log entry for a student's exit activities from the library."
    
    __tablename__ = 'exit_logs'
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True) # Primary key
    student_id: so.Mapped[str] = so.mapped_column(
        sa.ForeignKey('students.student_id', ondelete='CASCADE'),
        nullable=False) # Foreign key linking to the Student table
    timestamp: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, default=datetime.utcnow) # Timestamp of the log entry
    status: so.Mapped[str] = so.mapped_column(
        sa.String(20), nullable=False, default='OUT') # Status, default is 'OUT'

    student: so.Mapped[Student] = so.relationship(
        'Student',
        back_populates='exit_logs')  # Relationship to the Student model
