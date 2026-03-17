import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from backend.db import db
from backend.models import Link

dashboard_bp = Blueprint("dashboard", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@dashboard_bp.route("/dashboard")
@login_required
def index():
    links = Link.query.filter_by(user_id=current_user.id).order_by(Link.position).all()
    total_clicks = sum(link.click_count for link in links)
    return render_template("dashboard/index.html", links=links, total_clicks=total_clicks)


@dashboard_bp.route("/add-link", methods=["POST"])
@login_required
def add_link():
    title = request.form.get("title", "").strip()
    url = request.form.get("url", "").strip()

    if not title or not url:
        flash("Title and URL are required.")
        return redirect(url_for("dashboard.index"))

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    max_pos = db.session.query(db.func.max(Link.position)).filter_by(user_id=current_user.id).scalar() or 0
    link = Link(user_id=current_user.id, title=title, url=url, position=max_pos + 1)
    db.session.add(link)
    db.session.commit()
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/delete-link/<int:link_id>", methods=["POST"])
@login_required
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    if link.user_id != current_user.id:
        flash("Unauthorized.")
        return redirect(url_for("dashboard.index"))
    db.session.delete(link)
    db.session.commit()
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/reorder", methods=["POST"])
@login_required
def reorder():
    order = request.json.get("order", [])
    for index, link_id in enumerate(order):
        link = Link.query.get(link_id)
        if link and link.user_id == current_user.id:
            link.position = index
    db.session.commit()
    return jsonify({"status": "ok"})


@dashboard_bp.route("/update-profile", methods=["POST"])
@login_required
def update_profile():
    bio = request.form.get("bio", "").strip()
    current_user.bio = bio

    if "avatar" in request.files:
        file = request.files["avatar"]
        if file and file.filename and allowed_file(file.filename):
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)
            if size > MAX_FILE_SIZE:
                flash("Avatar must be under 2 MB.")
                return redirect(url_for("dashboard.index"))
            ext = file.filename.rsplit(".", 1)[1].lower()
            filename = f"{current_user.username}_{uuid.uuid4().hex[:8]}.{ext}"
            upload_dir = os.path.join(current_app.static_folder, "avatars")
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, filename))
            current_user.avatar = f"avatars/{filename}"

    db.session.commit()
    flash("Profile updated!")
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/update-theme", methods=["POST"])
@login_required
def update_theme():
    theme = request.form.get("theme", "dark")
    if theme not in ("dark", "neon", "professional"):
        theme = "dark"
    current_user.theme = theme
    db.session.commit()
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/update-domain", methods=["POST"])
@login_required
def update_domain():
    from backend.models import User
    domain = request.form.get("custom_domain", "").strip().lower()
    domain = domain.replace("https://", "").replace("http://", "").rstrip("/")

    if domain:
        existing = User.query.filter_by(custom_domain=domain).first()
        if existing and existing.id != current_user.id:
            flash("That domain is already in use.")
            return redirect(url_for("dashboard.index"))

    current_user.custom_domain = domain if domain else None
    db.session.commit()
    flash("Custom domain updated!")
    return redirect(url_for("dashboard.index"))
