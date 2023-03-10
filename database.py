import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

# ORM is SQLAlchemy
db = SQLAlchemy()

# this below is the structure for the table model. Nullable=false means it cannot be empty because if there is no
# content it can not be created.If there is no author added then n/a datetime doesn't work without first importing it
# at the top: from datetime import datetime
def to_tsvector_ix(*columns):
    s = " || ' ' || ".join(columns)
    return db.func.to_tsvector('slovenian', text(s))


class Category(db.Model):
    """model for BlogPost type of work (parrent)"""
    __tablename__ = "work_type"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class BlogPost(db.Model):
    """model for BlogPost (child)"""

    __tablename__ = "blog_post"
    __mapper_args__ = {"eager_defaults": True}

    # false means it must not be an empty value, default,"" means that there is nothing inside.
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(100), nullable=False, default="")
    content = db.Column(db.Text, nullable=False, default="")
    offer = db.Column(db.Text, nullable=False, default="")
    email = db.Column(db.Text, nullable=False, default="")
    confirmation_id = db.Column(db.Integer, nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    longitude = db.Column(db.Float, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    location = db.Column(db.String(255))

    # for categories
    category_id = db.Column(db.Integer, db.ForeignKey('work_type.id'), nullable=True)
    category = db.relationship('Category', backref=db.backref('work_type', lazy=True))

    # create full text search index
    __table_args__ = (
        Index(
            'idx_fulltext_title',
            db.func.to_tsvector('slovenian', title),
            postgresql_using='gin'
        ),
        Index(
            'idx_fulltext_content',
            db.func.to_tsvector('slovenian', content),
            postgresql_using='gin'
        ),
        Index(
            'idx_fulltext_offer',
            db.func.to_tsvector('slovenian', offer),
            postgresql_using='gin'
        ),
    )

    def __repr__(self):
        """returns object representative"""
        return 'Blog post ' + str(self.id)


class BlogApply(db.Model):
    """Database for apply"""

    __tablename__ = "blog_apply"
    __mapper_args__ = {"eager_defaults": True}

    id_apply = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_apply = db.Column(db.Text, nullable=False, default="")
    email_apply = db.Column(db.Text, nullable=False, default="")
    blog_post_id = db.Column(UUID(as_uuid=True), db.ForeignKey('blog_post.id'))
    apply_confirmation_id = db.Column(db.Integer, nullable=False)
    apply_confirmed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        """returns object representative"""
        return 'Blog apply ' + str(self.id_apply)

