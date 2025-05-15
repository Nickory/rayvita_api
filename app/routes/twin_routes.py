
from flask import Blueprint, request, jsonify
from datetime import datetime
from ..models import db, HealthTwin

bp = Blueprint('twin', __name__)

@bp.route('/add', methods=['POST'])
def add_twin():
    data = request.get_json() or {}
    t = HealthTwin(
        user_id=data['user_id'],
        snapshot_dt=data.get('snapshot_dt', datetime.utcnow()),
        avg_hr=data.get('avg_hr'),
        avg_hrv=data.get('avg_hrv'),
        stress_level=data.get('stress_level'),
        sleep_quality=data.get('sleep_quality'),
        tips_text=data.get('tips_text')
    )
    db.session.add(t)
    db.session.commit()
    return jsonify(msg='twin saved', twin_id=t.twin_id)

@bp.route('/user/<int:user_id>', methods=['GET'])
def list_twins(user_id):
    twins = HealthTwin.query.filter_by(user_id=user_id).order_by(HealthTwin.snapshot_dt.desc()).all()
    return jsonify([{
        "twin_id": t.twin_id,
        "snapshot_dt": str(t.snapshot_dt),
        "avg_hr": t.avg_hr,
        "avg_hrv": t.avg_hrv,
        "stress_level": t.stress_level,
        "sleep_quality": t.sleep_quality,
        "model_version": t.model_version,
        "tips_text": t.tips_text
    } for t in twins])
