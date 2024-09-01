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
    return db.session.get(User, int(id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(256), unique=True) 

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class BaseModel():
    __abstract__ = True
    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, default=datetime.utcnow)
    updated_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



class Student(db.Model, BaseModel):
    __tablename__ = 'students'

    student_id: so.Mapped[str] = so.mapped_column(
        sa.String(20), unique=True, nullable=False)
    fullname: so.Mapped[str] = so.mapped_column(sa.String(25), nullable=False)
    gender: so.Mapped[str] = so.mapped_column(sa.String(10), nullable=False)
    year: so.Mapped[str] = so.mapped_column(sa.String(25), nullable=False)
    department: so.Mapped[str] = so.mapped_column(sa.String(25), nullable=False)
    profile_img: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    total_library_time: so.Mapped[sa.types.Interval] = so.mapped_column(
        sa.types.Interval(), default=timedelta(seconds=0), nullable=False)

    laptop_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('laptops.id'), nullable=True)

    
    laptop: so.Mapped['Laptop'] = so.relationship(
        'Laptop', back_populates='student')

    logs: so.Mapped['LibLogs'] = so.relationship(
        'LibLogs',
        back_populates='student',
        cascade = 'all, delete-orphan',
        collection_class=list)

    def __repr__(self):
        return f'<Student {self.fullname}>'


class LaptopImage(db.Model):
    __tablename__ = 'laptop_images'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    laptop_in_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('laptops.id'), nullable=False)
    image_path: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)

    laptop: so.Mapped['Laptop'] = so.relationship('Laptop', back_populates='images')


class Laptop(db.Model, BaseModel):
    __tablename__ = 'laptops'

    laptop_unique_id: so.Mapped[int] = so.mapped_column(
        sa.Integer, unique=True, nullable=False)

    images: so.Mapped['LaptopImage'] = so.relationship(
        'LaptopImage',
        back_populates='laptop',
        cascade='all, delete-orphan',
        collection_class=list)
    student: so.Mapped['Student'] = so.relationship(
        'Student',
        back_populates='laptop',
        uselist=False,
        cascade='all, delete-orphan')

    def __init__(self):
        self.laptop_unique_id = self.generate_unique_laptop_id()

    def add_laptop_image(self, image_path):
        new_image = LaptopImage(image_path=image_path, laptop=self)
        self.images.append(new_image)
        db.session.add(new_image)

    @staticmethod
    def generate_unique_laptop_id():
        while 1:
            laptop_id = random.randint(10000, 99999)
            is_laptop_id_exist = db.session.scalar(
                sa.select(Laptop).where(Laptop.laptop_unique_id == laptop_id))
            if not is_laptop_id_exist:
                break
        return laptop_id

    def __repr__(self):
        return f'<Laptop {self.laptop_unique_id}>'



class LibLogs(db.Model):
    __tablename__ = 'lib_logs'
    id: so.Mapped['int'] = so.mapped_column(sa.Integer, primary_key=True)
    student_id: so.Mapped[str] = so.mapped_column(
        sa.ForeignKey('students.student_id'), nullable=False)
    timestamp: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, default=datetime.utcnow)
    status: so.Mapped[str] = so.mapped_column(
        sa.String(20), nullable=False)

    student: so.Mapped[Student] = so.relationship(
        'Student',
        back_populates='logs')
