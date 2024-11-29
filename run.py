from app import app
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.models import User, Student, Laptop, LaptopImage


@app.shell_context_processor
def make_shell_context():
    # Expose these objects in the Flask shell for easy access
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Student': Student, 'Laptop': Laptop, 'LaptopImage': LaptopImage}


