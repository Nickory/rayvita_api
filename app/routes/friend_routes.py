from flask import Blueprint, request, jsonify
from sqlalchemy import or_, and_
from ..models import db, FriendRequest, Friendship, Notification, User
from sqlalchemy.orm import joinedload

bp = Blueprint("friend", __name__, url_prefix="/api/friend")

# ========== 发送好友请求 ==========
@bp.route("/request", methods=["POST"])
def send_friend_request():
    data = request.get_json() or {}
    from_id = data.get("user_id")
    to_id = data.get("friend_id")

    # 参数验证
    if not from_id or not to_id or from_id == to_id:
        return jsonify(msg="Invalid parameters"), 400

    # 是否已存在好友关系
    exists = Friendship.query.filter(
        ((Friendship.user_id == from_id) & (Friendship.friend_id == to_id)) |
        ((Friendship.user_id == to_id) & (Friendship.friend_id == from_id))
    ).first()
    if exists:
        return jsonify(msg="Already friends"), 400

    # 是否已发起申请
    duplicate = FriendRequest.query.filter_by(from_user_id=from_id, to_user_id=to_id, status="pending").first()
    if duplicate:
        return jsonify(msg="Already requested"), 400

    fr = FriendRequest(from_user_id=from_id, to_user_id=to_id)
    db.session.add(fr)
    db.session.commit()

    notif = Notification(user_id=to_id, notif_type="friend",
                         content_txt=f"{from_id} sent you a friend request")
    db.session.add(notif)
    db.session.commit()

    return jsonify(msg="Request sent", request_id=fr.request_id), 200


# ========== 处理好友请求 ==========
@bp.route("/request/<int:req_id>", methods=["PUT"])
def handle_friend_request(req_id):
    req = FriendRequest.query.get_or_404(req_id)
    data = request.get_json() or {}
    action = data.get("action")  # "accept" or "reject"

    if req.status != "pending":
        return jsonify(msg="Already handled"), 400

    if action not in ("accept", "reject"):
        return jsonify(msg="Invalid action"), 400

    if action == "accept":
        # 添加好友记录（双向）
        f1 = Friendship(user_id=req.from_user_id, friend_id=req.to_user_id)
        db.session.add(f1)
    # 更新状态
    req.status = "accepted" if action == "accept" else "rejected"
    db.session.commit()

    return jsonify(msg=f"Request {action}ed"), 200

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
#好友申请列表 
@bp.route("/incoming", methods=["GET"])
def get_incoming_friend_requests():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify(error="Missing user_id"), 400

    requests = FriendRequest.query \
        .filter_by(to_user_id=user_id, status="pending") \
        .options(joinedload(FriendRequest.from_user)) \
        .all()

    result = []
    for req in requests:
        result.append({
            "request_id": req.request_id,
            "from_user_id": req.from_user_id,
            "to_user_id": req.to_user_id,
            "status": req.status,
            "created_at": req.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "from_user_nickname": req.from_user.nickname if req.from_user else None
        })

    return jsonify(requests=result), 200
