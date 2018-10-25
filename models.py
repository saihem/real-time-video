from . import db

class Response(db.Model):
    """
    Create a Department table
    """

    __tablename__ = 'response'

    id = db.Column(db.Integer, primary_key=True)
    response = db.Column(db.Text)
    time = db.Column(db.DateTime)
    type = db.Column(db.Integer, db.ForeignKey('response_type.id'))

    __table_args__ = (db.UniqueConstraint('id', 'time', name='_response_uc'),)

    def __repr__(self):
        return '<Department: {}>'.format(self.name)


class ResponseType(db.Model):
    """
    Create a Department table
    """

    __tablename__ = 'response_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)

    def __repr__(self):
        return '<Type: {}>'.format(self.name)