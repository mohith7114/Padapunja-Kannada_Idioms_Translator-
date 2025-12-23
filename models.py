# models.py
from extensions import db
from datetime import datetime

class Idiom(db.Model):
    __tablename__ = 'idioms'
    idiom = db.Column(db.String(255), primary_key=True)
    explanation_english = db.Column(db.Text, nullable=True)
    explanation_kannada = db.Column(db.Text)

    def to_dict(self):
        return {
            "idiom": self.idiom,
            "explanation_english": self.explanation_english,
            "explanation_kannada": self.explanation_kannada
        }

class History(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), index=True)
    original_sentence = db.Column(db.Text)
    status = db.Column(db.String(50))
    match_type = db.Column(db.String(50))
    idiom = db.Column(db.String(255))
    confidence = db.Column(db.Integer)
    translation = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "original_sentence": self.original_sentence,
            "status": self.status,
            "match_type": self.match_type,
            "idiom": self.idiom,
            "confidence": self.confidence,
            "translation": self.translation,
            "timestamp": self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

class Suggestion(db.Model):
    __tablename__ = 'suggestions'
    id = db.Column(db.Integer, primary_key=True)
    idiom = db.Column(db.String(255), nullable=False)
    explanation_kannada = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "idiom": self.idiom,
            "explanation_kannada": self.explanation_kannada,
            "timestamp": self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "email": self.email,
            "timestamp": self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }