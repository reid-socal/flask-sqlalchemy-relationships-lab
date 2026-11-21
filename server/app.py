#!/usr/bin/env python3

from flask import Flask, jsonify
from flask_migrate import Migrate

from models import db, Event, Session, Speaker, Bio

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)


def speaker_to_dict(speaker):
    """Format a Speaker (with bio text) as a dictionary.

    Falls back to "No bio available" when the speaker has no Bio.
    """
    return {
        "id": speaker.id,
        "name": speaker.name,
        "bio_text": speaker.bio.bio_text if speaker.bio else "No bio available",
    }


@app.route('/events')
def get_events():
    """Return all events as a list of dictionaries."""
    events = db.session.query(Event).all()
    return jsonify([
        {"id": event.id, "name": event.name, "location": event.location}
        for event in events
    ]), 200


@app.route('/events/<int:id>/sessions')
def get_event_sessions(id):
    """Return all sessions for one event, or 404 if the event is missing."""
    event = db.session.get(Event, id)
    if event is None:
        return jsonify({"error": "Event not found"}), 404

    return jsonify([
        {
            "id": session.id,
            "title": session.title,
            "start_time": session.start_time.isoformat() if session.start_time else None,
        }
        for session in event.sessions
    ]), 200


@app.route('/speakers')
def get_speakers():
    """Return all speakers as a list of dictionaries (id and name)."""
    speakers = db.session.query(Speaker).all()
    return jsonify([
        {"id": speaker.id, "name": speaker.name}
        for speaker in speakers
    ]), 200


@app.route('/speakers/<int:id>')
def get_speaker(id):
    """Return one speaker with their bio, or 404 if the speaker is missing."""
    speaker = db.session.get(Speaker, id)
    if speaker is None:
        return jsonify({"error": "Speaker not found"}), 404

    return jsonify(speaker_to_dict(speaker)), 200


@app.route('/sessions/<int:id>/speakers')
def get_session_speakers(id):
    """Return all speakers (with bios) for one session, or 404 if missing."""
    session = db.session.get(Session, id)
    if session is None:
        return jsonify({"error": "Session not found"}), 404

    return jsonify([speaker_to_dict(speaker) for speaker in session.speakers]), 200


if __name__ == '__main__':
    app.run(port=5555, debug=True)