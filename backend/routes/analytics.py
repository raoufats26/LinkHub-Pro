from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from backend.models import Click, Link
from backend.db import db
from sqlalchemy import func

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/analytics-data")
@login_required
def analytics_data():
    data = (
        db.session.query(
            func.date(Click.timestamp),
            func.count(Click.id)
        )
        .join(Link, Link.id == Click.link_id)
        .filter(Link.user_id == current_user.id)
        .group_by(func.date(Click.timestamp))
        .all()
    )
    return jsonify({
        "labels": [str(d[0]) for d in data],
        "values": [d[1] for d in data]
    })
