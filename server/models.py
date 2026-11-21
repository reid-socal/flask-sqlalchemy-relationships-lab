from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

# Association table for the many-to-many relationship between Session and Speaker.
# It holds only two foreign keys (no extra data), so a plain Table is used
# instead of a full model. The pair of columns is the composite primary key,
# which prevents the same speaker from being linked to the same session twice.
session_speakers = db.Table(
    'session_speakers',
    db.Column('session_id', db.Integer, db.ForeignKey('sessions.id'), primary_key=True),
    db.Column('speaker_id', db.Integer, db.ForeignKey('speakers.id'), primary_key=True),
)


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)

    # One-to-many: an Event has many Sessions.
    # cascade='all, delete-orphan' -> deleting an Event deletes its Sessions.
    sessions = db.relationship(
        'Session',
        back_populates='event',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Event {self.id}, {self.name}, {self.location}>'


class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    start_time = db.Column(db.DateTime)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    # Many-to-one: a Session belongs to one Event.
    event = db.relationship('Event', back_populates='sessions')

    # Many-to-many: a Session has many Speakers through session_speakers.
    speakers = db.relationship(
        'Speaker',
        secondary=session_speakers,
        back_populates='sessions'
    )

    def __repr__(self):
        return f'<Session {self.id}, {self.title}, {self.start_time}>'


class Speaker(db.Model):
    __tablename__ = 'speakers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    # One-to-one: a Speaker has one Bio (uselist=False returns a single
    # object instead of a list).
    # cascade='all, delete-orphan' -> deleting a Speaker deletes their Bio.
    bio = db.relationship(
        'Bio',
        back_populates='speaker',
        uselist=False,
        cascade='all, delete-orphan'
    )

    # Many-to-many: a Speaker has many Sessions through session_speakers.
    sessions = db.relationship(
        'Session',
        secondary=session_speakers,
        back_populates='speakers'
    )

    def __repr__(self):
        return f'<Speaker {self.id}, {self.name}>'


class Bio(db.Model):
    __tablename__ = 'bios'

    id = db.Column(db.Integer, primary_key=True)
    bio_text = db.Column(db.Text, nullable=False)
    speaker_id = db.Column(db.Integer, db.ForeignKey('speakers.id'))

    # One-to-one (child side): a Bio belongs to one Speaker.
    speaker = db.relationship('Speaker', back_populates='bio')

    def __repr__(self):
        return f'<Bio {self.id}, {self.bio_text}>'