from flask import Blueprint, request, jsonify
from sqlalchemy import or_, and_
from ..models import db, FriendRequest, Friendship, Notification, User

bp = Blueprint("friend", __name__, url_prefix="/api/friend")

# 3‑1 发送好友请求
@bp.route("/request", methods=["POST"])
def send_request():
    data = request.get_json() or {}
    fr = FriendRequest(from_id=data["user_id"], to_id=data["friend_id"])
    db.session.add(fr)
    db.session.commit()
    # 通知
    notif = Notification(user_id=data["friend_id"], notif_type="friend",
                         content_txt=f"{data['user_id']} sent you a friend request")
    db.session.add(notif)
    db.session.commit()
    return jsonify(msg="request sent", request_id=fr.req_id), 200

# 3‑2 处理好友请求
@bp.route("/request/<int:req_id>", methods=["PUT"])
def handle_request(req_id):
    req = FriendRequest.query.get_or_404(req_id)
    action = (request.get_json() or {}).get("action")
    if action not in ("accept", "reject"):
        return jsonify(msg="invalid action"), 400
    req.status = "accepted" if action == "accept" else "rejected"
    if action == "accept":
        f = Friendship(user_id=req.from_id, friend_id=req.to_id)
        db.session.add(f)
    db.session.commit()
    return jsonify(msg=action), 200

# 3‑3 好友列表
@bp.route("/list", methods=["GET"])
def list_friends():
    user_id = request.args.get("user_id", type=int)
    rels = Friendship.query.filter(
        or_(Friendship.user_id == user_id, Friendship.friend_id == user_id),
        Friendship.is_blocked == False
    ).all()
    friend_ids = [r.friend_id if r.user_id == user_id else r.user_id for r in rels]
    users = User.query.filter(User.user_id.in_(friend_ids)).all()
    return jsonify([{"user_id":u.user_id,"nickname":u.nickname} for u in users])

# 3‑4 拉黑 / 解除拉黑
@bp.route("/<int:friend_id>/block", methods=["PUT"])
def block_friend(friend_id):
    user_id = (request.get_json() or {}).get("user_id")
    f = Friendship.query.filter(
        or_(and_(Friendship.user_id==user_id, Friendship.friend_id==friend_id),
            and_(Friendship.user_id==friend_id, Friendship.friend_id==user_id))
    ).first_or_404()
    f.is_blocked = (request.get_json() or {}).get("block", True)
    db.session.commit()
    return jsonify(msg="blocked", blocked=f.is_blocked)
