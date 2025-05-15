
from . import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(50))
    avatar_url = db.Column(db.String(500))
    theme_pref = db.Column(db.Enum('light','dark','R'), default='light')
    registration_dt = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_dt = db.Column(db.DateTime)
    status = db.Column(db.Enum('active', 'deactivated'), default='active')
    device_info = db.Column(db.String(255))

    sessions = db.relationship('CaptureSession', backref='user', lazy=True)

class CaptureSession(db.Model):
    __tablename__ = 'capture_sessions'
    session_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    start_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_dt = db.Column(db.DateTime)
    device_info = db.Column(db.String(255))
    illumination = db.Column(db.Float)
    sampling_rate = db.Column(db.Integer, default=30)
    notes = db.Column(db.Text)

    rppg_samples = db.relationship('RPPGSample', backref='session', cascade='all,delete', lazy=True)

class RPPGSample(db.Model):
    __tablename__ = 'rppg_samples'
    sample_id = db.Column(db.BigInteger, primary_key=True)
    session_id = db.Column(db.BigInteger, db.ForeignKey('capture_sessions.session_id', ondelete='CASCADE'), nullable=False)
    ts = db.Column(db.DateTime, nullable=False)
    heart_rate = db.Column(db.Float)
    hrv = db.Column(db.Float)
    raw_signal_url = db.Column(db.String(500))

class HealthTwin(db.Model):
    __tablename__ = 'health_twin'
    twin_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    snapshot_dt = db.Column(db.DateTime, default=datetime.utcnow)
    avg_hr = db.Column(db.Float)
    avg_hrv = db.Column(db.Float)
    stress_level = db.Column(db.Enum('low','medium','high'), default='medium')
    sleep_quality = db.Column(db.Enum('good','normal','poor'), default='normal')
    model_version = db.Column(db.String(20), default='v1.0')
    tips_text = db.Column(db.Text)

class HealthTip(db.Model):
    __tablename__ = 'health_tips'
    tip_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    tip_dt = db.Column(db.DateTime, default=datetime.utcnow)
    tip_text = db.Column(db.Text, nullable=False)
    tip_source = db.Column(db.Enum('AI','rule'), default='AI')
    push_method = db.Column(db.Enum('popup','notification','email'), default='popup')
