from flask import Blueprint, jsonify, request
from server.models.users import Users
from server.extensions import db

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/money", methods=["GET"])
def get_user_money():
    user_id = 1  # We only support a single user right now

    # Fetch user by id
    user = Users.query.get(user_id)

    if not user:
        return jsonify({"error": f"User with ID {user_id} not found"}), 404

    # Return the user's money
    return jsonify({"money": user.money}), 200


# This app is only intended to support one user at the moment
# Initialize with this route
@user_bp.route("/init_user", methods=["POST"])
def init_user():
    existing_user = Users.query.get(1)

    if existing_user:
        return "User with ID 1 already exists, no new user created."

    new_user = Users(id=1, username="alex", money=1000000.00)
    db.session.add(new_user)
    db.session.commit()

    return "New user initialized"


@user_bp.route("/delete_all_users", methods=["DELETE"])
def delete_all_users():
    Users.query.delete()
    db.session.commit()
