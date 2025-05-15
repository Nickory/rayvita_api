
from flask import Blueprint, request, jsonify
from datetime import datetime
from ..models import db, HealthTip

bp = Blueprint('tips', __name__)

@bp.route('/add', methods=['POST'])
def add_tip():
    data = request.get_json() or {}
    tip = HealthTip(
        user_id=data['user_id'],
        tip_dt=data.get('tip_dt', datetime.utcnow()),
        tip_text=data['tip_text'],
        tip_source=data.get('tip_source','AI'),
        push_method=data.get('push_method','popup')
    )
    db.session.add(tip)
    db.session.commit()
    return jsonify(msg='tip added', tip_id=tip.tip_id)

@bp.route('/user/<int:user_id>', methods=['GET'])
def list_tips(user_id):
    tips = HealthTip.query.filter_by(user_id=user_id).order_by(HealthTip.tip_dt.desc()).all()
    return jsonify([{
        "tip_id": t.tip_id,
        "tip_dt": str(t.tip_dt),
        "tip_text": t.tip_text,
        "tip_source": t.tip_source,
        "push_method": t.push_method
    } for t in tips])
