
from . import db
from datetime import datetime

from sqlalchemy.orm import relationship

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

#二期api



    # 业务逻辑：不让自己加自己
    __table_args__ = (db.CheckConstraint('user_id <> friend_id', name='chk_not_self'),)

class Challenge(db.Model):
    __tablename__ = 'challenges'
    challenge_id   = db.Column(db.BigInteger, primary_key=True)
    user_id        = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    challenge_type = db.Column(db.Enum('hr_stability', 'steps', 'meditation', name='challenge_type'), default='hr_stability')
    start_dt       = db.Column(db.DateTime, default=datetime.utcnow)
    end_dt         = db.Column(db.DateTime)
    score          = db.Column(db.Float, default=0)
    punch_count    = db.Column(db.Integer, default=0)
    rule_version   = db.Column(db.String(20), default='v1.0')

#三期

class Friendship(db.Model):
    __tablename__ = 'friendships'
    friendship_id = db.Column(db.BigInteger, primary_key=True)
    user_id       = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    friend_id     = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    is_blocked    = db.Column(db.Boolean, default=False)
    created_dt    = db.Column(db.DateTime, default=datetime.utcnow)



class FriendRequest(db.Model):
    __tablename__ = "friend_requests"

    request_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    from_user_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id"), nullable=False)
    to_user_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id"), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    status = db.Column(db.Enum("pending", "accepted", "rejected"), default="pending")

    from_user = relationship("User", foreign_keys=[from_user_id])  

class Post(db.Model):
    __tablename__ = 'posts'
    post_id        = db.Column(db.BigInteger, primary_key=True)
    user_id        = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    post_dt        = db.Column(db.DateTime, default=datetime.utcnow)
    post_type      = db.Column(db.Enum('moment','challenge','summary'), default='moment')
    text_content   = db.Column(db.Text)
    image_url      = db.Column(db.String(500))
    like_count     = db.Column(db.Integer, default=0)
    comment_count  = db.Column(db.Integer, default=0)
    review_status  = db.Column(db.Enum('pending','approved','rejected'), default='approved')

class PostLike(db.Model):
    __tablename__ = 'post_likes'
    like_id   = db.Column(db.BigInteger, primary_key=True)
    post_id   = db.Column(db.BigInteger, db.ForeignKey('posts.post_id'), nullable=False)
    user_id   = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    like_dt   = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='uk_like'),)

class PostComment(db.Model):
    __tablename__ = 'post_comments'
    comment_id    = db.Column(db.BigInteger, primary_key=True)
    post_id       = db.Column(db.BigInteger, db.ForeignKey('posts.post_id'), nullable=False)
    user_id       = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    comment_dt    = db.Column(db.DateTime, default=datetime.utcnow)
    comment_text  = db.Column(db.Text, nullable=False)

class Notification(db.Model):
    __tablename__ = 'notifications'
    notif_id     = db.Column(db.BigInteger, primary_key=True)
    user_id      = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    notif_type   = db.Column(db.Enum('system','friend','health'), default='system')
    content_txt  = db.Column(db.Text, nullable=False)
    created_dt   = db.Column(db.DateTime, default=datetime.utcnow)
    is_read      = db.Column(db.Boolean, default=False)
    push_channel = db.Column(db.Enum('inapp','email','sms'), default='inapp')
