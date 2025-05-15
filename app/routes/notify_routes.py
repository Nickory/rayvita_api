from flask import Blueprint, request, jsonify
from ..models import db, Notification

bp = Blueprint("notify", __name__, url_prefix="/api/notify")

# 3‑13 通知列表
@bp.route("/list", methods=["GET"])
def list_notif():
    user_id = request.args.get("user_id", type=int)
    unread  = request.args.get("unread", type=str) == "true"
    q = Notification.query.filter_by(user_id=user_id)
    if unread: q = q.filter_by(is_read=False)
    n = q.order_by(Notification.created_dt.desc()).all()
    return jsonify([{
        "notif_id":x.notif_id,
        "content_txt":x.content_txt,
        "created_dt":str(x.created_dt),
        "is_read":x.is_read
    } for x in n])

# 3‑14 标记已读
@bp.route("/<int:notif_id>/read", methods=["PUT"])
def mark_read(notif_id):
    n = Notification.query.get_or_404(notif_id)
    n.is_read = True
    db.session.commit()
    return jsonify(read=True)
