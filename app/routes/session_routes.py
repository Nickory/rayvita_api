
from flask import Blueprint, request, jsonify
from datetime import datetime
from ..models import db, CaptureSession

bp = Blueprint('session', __name__)

@bp.route('/create', methods=['POST'])
def create_session():
    data = request.get_json() or {}
    s = CaptureSession(
        user_id=data['user_id'],
        start_dt=data.get('start_dt', datetime.utcnow()),
        device_info=data.get('device_info'),
        illumination=data.get('illumination'),
        sampling_rate=data.get('sampling_rate', 30),
        notes=data.get('notes')
    )
    db.session.add(s)
    db.session.commit()
    return jsonify(msg='session created', session_id=s.session_id), 200

@bp.route('/<int:session_id>', methods=['PUT'])
def update_session(session_id):
    s = CaptureSession.query.get_or_404(session_id)
    data = request.get_json() or {}
    s.end_dt = data.get('end_dt', s.end_dt)
    s.notes = data.get('notes', s.notes)
    db.session.commit()
    return jsonify(msg='updated')

@bp.route('/user/<int:user_id>', methods=['GET'])
def list_sessions(user_id):
    sessions = CaptureSession.query.filter_by(user_id=user_id).order_by(CaptureSession.start_dt.desc()).all()
    return jsonify([{
        "session_id": s.session_id,
        "start_dt": str(s.start_dt),
        "end_dt": str(s.end_dt) if s.end_dt else None,
        "device_info": s.device_info,
        "illumination": s.illumination,
        "sampling_rate": s.sampling_rate,
        "notes": s.notes
    } for s in sessions])
