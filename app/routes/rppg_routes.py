
from flask import Blueprint, request, jsonify
from datetime import datetime
from ..models import db, RPPGSample, CaptureSession

bp = Blueprint('rppg', __name__)

def _sample_to_dict(s):
    return {
        "sample_id": s.sample_id,
        "session_id": s.session_id,
        "ts": str(s.ts),
        "heart_rate": s.heart_rate,
        "hrv": s.hrv,
        "raw_signal_url": s.raw_signal_url
    }

@bp.route('/add', methods=['POST'])
def add_sample():
    data = request.get_json() or {}
    session = CaptureSession.query.get_or_404(data['session_id'])
    s = RPPGSample(
        session_id=session.session_id,
        ts=data.get('ts', datetime.utcnow()),
        heart_rate=data.get('heart_rate'),
        hrv=data.get('hrv'),
        raw_signal_url=data.get('raw_signal_url')
    )
    db.session.add(s)
    db.session.commit()
    return jsonify(msg='sample added', sample_id=s.sample_id)

@bp.route('/<int:sample_id>', methods=['PUT'])
def update_sample(sample_id):
    s = RPPGSample.query.get_or_404(sample_id)
    data = request.get_json() or {}
    s.heart_rate = data.get('heart_rate', s.heart_rate)
    s.hrv = data.get('hrv', s.hrv)
    s.raw_signal_url = data.get('raw_signal_url', s.raw_signal_url)
    db.session.commit()
    return jsonify(msg='sample updated')

@bp.route('/<int:sample_id>', methods=['DELETE'])
def delete_sample(sample_id):
    s = RPPGSample.query.get_or_404(sample_id)
    db.session.delete(s)
    db.session.commit()
    return jsonify(msg='sample deleted')

@bp.route('/session/<int:session_id>', methods=['GET'])
def list_samples_by_session(session_id):
    samples = RPPGSample.query.filter_by(session_id=session_id).order_by(RPPGSample.ts).all()
    return jsonify([_sample_to_dict(s) for s in samples])
