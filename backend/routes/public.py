from flask import Blueprint, render_template, redirect, request, abort
from backend.models import User, Link, Click
from backend.db import db

public_bp = Blueprint("public", __name__)

_RESERVED = frozenset([
    "static", "favicon.ico", "robots.txt", "dashboard", "add-link",
    "delete-link", "reorder", "update-profile", "update-theme",
    "update-domain", "analytics-data", "register", "login", "logout",
    "go", "qr-code",
])


@public_bp.route("/<username>")
def profile(username):
    if username in _RESERVED:
        abort(404)

    # Custom-domain resolution
    host = request.host.split(":")[0]
    domain_user = User.query.filter_by(custom_domain=host).first()
    user = domain_user if domain_user else User.query.filter_by(username=username).first_or_404()

    links = Link.query.filter_by(user_id=user.id).order_by(Link.position).all()
    return render_template("public/profile.html", user=user, links=links)


@public_bp.route("/go/<int:link_id>")
def go(link_id):
    link = Link.query.get_or_404(link_id)
    link.click_count += 1
    click = Click(link_id=link.id, ip_address=request.remote_addr)
    db.session.add(click)
    db.session.commit()
    return redirect(link.url)
