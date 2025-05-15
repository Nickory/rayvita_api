from flask import Blueprint, request, jsonify
from ..models import db, Post, PostLike, PostComment

bp = Blueprint("post", __name__, url_prefix="/api/post")

def _post_dict(p):
    return {
        "post_id": p.post_id,
        "user_id": p.user_id,
        "post_dt": str(p.post_dt),
        "text_content": p.text_content,
        "image_url": p.image_url,
        "like_count": p.like_count,
        "comment_count": p.comment_count
    }

# 3‑5 发表动态
@bp.route("/create", methods=["POST"])
def create_post():
    d = request.get_json() or {}
    p = Post(user_id=d["user_id"],
             text_content=d.get("text_content"),
             image_url=d.get("image_url"),
             post_type=d.get("post_type","moment"))
    db.session.add(p)
    db.session.commit()
    return jsonify(msg="posted", post_id=p.post_id), 200

# 3‑6 删除动态
@bp.route("/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    p = Post.query.get_or_404(post_id)
    db.session.delete(p)
    db.session.commit()
    return jsonify(msg="deleted")

# 3‑7 动态详情
@bp.route("/<int:post_id>", methods=["GET"])
def get_post(post_id):
    return jsonify(_post_dict(Post.query.get_or_404(post_id)))

# 3‑8 时间线
@bp.route("/feed", methods=["GET"])
def feed():
    scope = request.args.get("scope","all")
    user_id = request.args.get("user_id", type=int)
    query = Post.query
    if scope=="friends":
        from ..models import Friendship
        ids = db.session.query(Friendship.friend_id).filter_by(user_id=user_id)
        query = query.filter(Post.user_id.in_(ids))
    posts = query.order_by(Post.post_dt.desc()).limit(50).all()
    return jsonify([_post_dict(p) for p in posts])

# 3‑9 点赞 / 取消
@bp.route("/<int:post_id>/like", methods=["POST","DELETE"])
def like(post_id):
    user_id = (request.get_json() or {}).get("user_id")
    if request.method=="POST":
        if not PostLike.query.filter_by(post_id=post_id,user_id=user_id).first():
            db.session.add(PostLike(post_id=post_id,user_id=user_id))
            Post.query.get(post_id).like_count += 1
    else:
        like = PostLike.query.filter_by(post_id=post_id,user_id=user_id).first_or_404()
        db.session.delete(like)
        Post.query.get(post_id).like_count -= 1
    db.session.commit()
    return jsonify(liked=request.method=="POST")

# 3‑10 评论
@bp.route("/<int:post_id>/comment", methods=["POST"])
def comment(post_id):
    d = request.get_json() or {}
    c = PostComment(post_id=post_id, user_id=d["user_id"], comment_text=d["comment_text"])
    db.session.add(c)
    Post.query.get(post_id).comment_count += 1
    db.session.commit()
    return jsonify(msg="commented", comment_id=c.comment_id)

# 3‑11 删除评论
@bp.route("/comment/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    c = PostComment.query.get_or_404(comment_id)
    post = Post.query.get(c.post_id)
    post.comment_count -= 1
    db.session.delete(c)
    db.session.commit()
    return jsonify(msg="comment deleted")

# 3‑12 评论列表
@bp.route("/<int:post_id>/comments", methods=["GET"])
def list_comments(post_id):
    cs = PostComment.query.filter_by(post_id=post_id).order_by(PostComment.comment_dt).all()
    return jsonify([{
        "comment_id":c.comment_id,"user_id":c.user_id,
        "comment_dt":str(c.comment_dt),"comment_text":c.comment_text
    } for c in cs])
