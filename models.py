from . import db
import datetime
import decimal
from sqlalchemy.sql.expression import ClauseElement

def get_or_create(session, model, defaults=None, **kwargs):
    try:
        instance = session.query(model).filter_by(**kwargs).first()
    except AttributeError:
        instance = None
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.items() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        session.commit()
        return instance, True

def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)


class Response(db.Model):
    """
    Create a Department table
    """

    __tablename__ = 'response'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    response = db.Column(db.Text, nullable=True)
    time = db.Column(db.DateTime, default=datetime.datetime.now)
    type_id = db.Column(db.Integer, db.ForeignKey('response_type.id'), nullable=False)
    type = db.relationship("ResponseType", lazy='joined')

    def __repr__(self):
        return '<Response: {}>'.format(self.response)


class ResponseType(db.Model):
    """
    Create a Department table
    """

    __tablename__ = 'response_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), )

    def __repr__(self):
        return '<Type: {}>'.format(self.name)