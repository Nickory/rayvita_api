from datetime import datetime
from flask import Blueprint, request, jsonify
from ..models import db, Challenge

bp = Blueprint('challenge', __name__)

# 创建挑战
@bp.route('/create', methods=['POST'])
def create_challenge():
    d = request.get_json(force=True)
    ch = Challenge(
        user_id=d['user_id'],
        challenge_type=d.get('challenge_type', 'hr_stability'),
        start_dt=datetime.utcnow(),
        rule_version=d.get('rule_version', 'v1.0')
    )
    db.session.add(ch)
    db.session.commit()
    return jsonify(msg='challenge created', challenge_id=ch.challenge_id), 200

# 每日打卡
@bp.route('/punch', methods=['POST'])
def punch():
    d = request.get_json(force=True)
    ch = Challenge.query.get_or_404(d['challenge_id'])
    ch.score += float(d.get('value', 0))
    ch.punch_count += 1
    db.session.commit()
    return jsonify(msg='check-in ok', total_score=ch.score, punch_count=ch.punch_count)

# 结束挑战 / 修改
@bp.route('/<int:cid>', methods=['PUT'])
def close_challenge(cid):
    ch = Challenge.query.get_or_404(cid)
    body = request.get_json(force=True)
    ch.end_dt = body.get('end_dt', datetime.utcnow())
    db.session.commit()
    return jsonify(msg='challenge closed')

# 按用户查询
@bp.route('/user/<int:user_id>', methods=['GET'])
def list_user_challenges(user_id):
    qs = Challenge.query.filter_by(user_id=user_id).order_by(Challenge.start_dt.desc()).all()
    return jsonify([{
        "challenge_id": c.challenge_id,
        "type":         c.challenge_type,
        "start_dt":     c.start_dt.isoformat(),
        "end_dt":       c.end_dt.isoformat() if c.end_dt else None,
        "score":        c.score,
        "punch_count":  c.punch_count
    } for c in qs])
