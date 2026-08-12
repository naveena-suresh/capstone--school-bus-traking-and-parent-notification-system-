from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection


auth = Blueprint("auth", __name__)


# ==============================
# SIGNUP
# ==============================

@auth.route("/api/signup", methods=["POST"])
def signup():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:

        return jsonify({
            "success": False,
            "message": "Please fill all fields"
        }), 400

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:

        connection.close()

        return jsonify({
            "success": False,
            "message": "Email already registered"
        }), 400

    password_hash = generate_password_hash(password)

    cursor.execute("""
        INSERT INTO users
        (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        email,
        password_hash,
        "parent"
    ))

    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Signup successful"
    })


# ==============================
# LOGIN
# ==============================

@auth.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:

        return jsonify({
            "success": False,
            "message": "Email and password required"
        }), 400

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    )

    user = cursor.fetchone()

    connection.close()

    if user and check_password_hash(
        user["password"],
        password
    ):

        session["user_id"] = user["user_id"]
        session["user_name"] = user["name"]
        session["role"] = user["role"]

        return jsonify({
            "success": True,
            "message": "Login successful",
            "name": user["name"]
        })

    return jsonify({
        "success": False,
        "message": "Invalid email or password"
    }), 401


# ==============================
# LOGOUT
# ==============================

@auth.route("/api/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "success": True,
        "message": "Logout successful"
    })


# ==============================
# CURRENT USER
# ==============================

@auth.route("/api/me")
def current_user():

    if "user_id" not in session:

        return jsonify({
            "logged_in": False
        })

    return jsonify({
        "logged_in": True,
        "user_id": session["user_id"],
        "name": session["user_name"],
        "role": session["role"]
    })