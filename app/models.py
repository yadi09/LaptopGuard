from typing import Optional
from app import db
import sqlalchemy as sa
import sqlalchemy.orm as so


class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), unique=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
