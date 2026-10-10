import os
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2
from functools import wraps

from flask import (
    Flask, jsonify, request, send_from_directory,
    session, redirect
)
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_connection, initialize_database

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "school-bus-development-key")

BASE_DIR = Path(__file__).resolve().parent

initialize_database()


# ---------------- AUTHENTICATION ----------------

def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({
                "success": False,
                "message": "Please login first."
            }), 401
        return function(*args, **kwargs)
    return wrapper


# ---------------- HTML PAGES ----------------

@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "login.html")


@app.route("/login")
def login_page():
    return send_from_directory(BASE_DIR, "login.html")


@app.route("/signin")
def signin_page():
    return send_from_directory(BASE_DIR, "signin.html")


@app.route("/dashboard")
def dashboard_page():
    if "user_id" not in session:
        return redirect("/login")
    return send_from_directory(BASE_DIR, "index.html")


# ---------------- REGISTER ACCOUNT ----------------

@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or len(password) < 6:
        return jsonify({
            "success": False,
            "message": "Enter name, email and a password of at least 6 characters."
        }), 400

    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                email,
                generate_password_hash(password),
                "Parent"
            )
        )
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Account created successfully."
        })

    except Exception:
        conn.rollback()
        return jsonify({
            "success": False,
            "message": "Email already exists or registration failed."
        }), 409

    finally:
        conn.close()


# ---------------- LOGIN ----------------

@app.route("/api/signin", methods=["POST"])
def signin():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    conn = get_connection()

    try:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid email or password."
            }), 401

        stored_password = user["password"]

        try:
            valid = check_password_hash(stored_password, password)
        except (ValueError, TypeError):
            valid = False

        # Support accounts created by an older version.
        if not valid and stored_password == password:
            valid = True

            conn.execute(
                "UPDATE users SET password = ? WHERE user_id = ?",
                (
                    generate_password_hash(password),
                    user["user_id"]
                )
            )
            conn.commit()

        if not valid:
            return jsonify({
                "success": False,
                "message": "Invalid email or password."
            }), 401

        session.clear()
        session["user_id"] = user["user_id"]
        session["name"] = user["name"]
        session["role"] = user["role"]

        return jsonify({
            "success": True,
            "message": "Login successful."
        })

    finally:
        conn.close()


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


@app.route("/api/me")
@login_required
def get_me():
    return jsonify({
        "success": True,
        "user": {
            "user_id": session["user_id"],
            "name": session["name"],
            "role": session["role"]
        }
    })


# ---------------- SAVE STUDENT AND BUS ----------------

@app.route("/api/save-details", methods=["POST"])
@login_required
def save_details():
    data = request.get_json(silent=True) or {}

    student = data.get("student", "").strip()
    student_code = data.get("studentId", "").strip()
    bus_number = data.get("bus", "").strip()
    driver = data.get("driver", "").strip()
    stop_name = data.get("location", "").strip()
    route_name = data.get("route", "").strip()

    if not student or not bus_number or not stop_name:
        return jsonify({
            "success": False,
            "message": "Student name, bus number and stop are required."
        }), 400

    conn = get_connection()

    try:
        bus = conn.execute(
            "SELECT bus_id FROM buses WHERE bus_number = ?",
            (bus_number,)
        ).fetchone()

        if bus:
            bus_id = bus["bus_id"]

            conn.execute(
                """
                UPDATE buses
                SET driver_name = ?, route_name = ?
                WHERE bus_id = ?
                """,
                (driver, route_name, bus_id)
            )
        else:
            cursor = conn.execute(
                """
                INSERT INTO buses
                (bus_number, driver_name, route_name, status)
                VALUES (?, ?, ?, ?)
                """,
                (bus_number, driver, route_name, "Waiting")
            )
            bus_id = cursor.lastrowid

        existing = None

        if student_code:
            existing = conn.execute(
                """
                SELECT student_id FROM students
                WHERE student_code = ? AND parent_id = ?
                """,
                (student_code, session["user_id"])
            ).fetchone()

        if existing:
            conn.execute(
                """
                UPDATE students
                SET name = ?, bus_id = ?, stop_name = ?
                WHERE student_id = ?
                """,
                (
                    student,
                    bus_id,
                    stop_name,
                    existing["student_id"]
                )
            )
        else:
            conn.execute(
                """
                INSERT INTO students
                (student_code, name, parent_id, bus_id, stop_name)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    student_code or None,
                    student,
                    session["user_id"],
                    bus_id,
                    stop_name
                )
            )

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Student and bus details saved successfully."
        })

    except Exception as error:
        conn.rollback()
        app.logger.exception("Saving details failed")
        return jsonify({
            "success": False,
            "message": "Unable to save details. Check the application log."
        }), 500

    finally:
        conn.close()


# ---------------- STUDENT DETAILS ----------------

@app.route("/api/student")
@login_required
def get_student():
    conn = get_connection()

    try:
        student = conn.execute(
            """
            SELECT
                s.student_id,
                s.student_code,
                s.name AS student,
                s.stop_name AS location,
                u.name AS parent,
                b.bus_number AS bus,
                b.driver_name AS driver,
                b.route_name AS route
            FROM students s
            LEFT JOIN users u ON s.parent_id = u.user_id
            LEFT JOIN buses b ON s.bus_id = b.bus_id
            WHERE s.parent_id = ?
            ORDER BY s.student_id DESC
            LIMIT 1
            """,
            (session["user_id"],)
        ).fetchone()

        return jsonify(dict(student) if student else {})

    finally:
        conn.close()


# ---------------- BUS DETAILS ----------------

@app.route("/api/bus")
@login_required
def get_bus():
    conn = get_connection()

    try:
        bus = conn.execute(
            """
            SELECT b.*
            FROM buses b
            JOIN students s ON s.bus_id = b.bus_id
            WHERE s.parent_id = ?
            ORDER BY s.student_id DESC
            LIMIT 1
            """,
            (session["user_id"],)
        ).fetchone()

        return jsonify(dict(bus) if bus else {})

    finally:
        conn.close()


# ---------------- UPDATE GPS LOCATION ----------------

@app.route("/api/update-location", methods=["POST"])
@login_required
def update_location():
    data = request.get_json(silent=True) or {}

    try:
        latitude = float(data["latitude"])
        longitude = float(data["longitude"])
        speed = float(data.get("speed", 0) or 0)
    except (KeyError, ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Valid latitude and longitude are required."
        }), 400

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return jsonify({
            "success": False,
            "message": "Coordinates are invalid."
        }), 400

    conn = get_connection()

    try:
        bus = conn.execute(
            """
            SELECT b.bus_id
            FROM buses b
            JOIN students s ON s.bus_id = b.bus_id
            WHERE s.parent_id = ?
            ORDER BY s.student_id DESC
            LIMIT 1
            """,
            (session["user_id"],)
        ).fetchone()

        if not bus:
            return jsonify({
                "success": False,
                "message": "Save bus and student details first."
            }), 404

        bus_id = bus["bus_id"]

        conn.execute(
            """
            UPDATE buses
            SET latitude = ?, longitude = ?, status = ?
            WHERE bus_id = ?
            """,
            (latitude, longitude, "On the way", bus_id)
        )

        conn.execute(
            """
            INSERT INTO bus_locations
            (bus_id, latitude, longitude, speed)
            VALUES (?, ?, ?, ?)
            """,
            (bus_id, latitude, longitude, speed)
        )

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Bus location updated successfully."
        })

    except Exception:
        conn.rollback()
        app.logger.exception("GPS update failed")
        return jsonify({
            "success": False,
            "message": "Unable to update location."
        }), 500

    finally:
        conn.close()


# ---------------- GET CURRENT LOCATION ----------------

@app.route("/api/location")
@login_required
def get_location():
    conn = get_connection()

    try:
        location = conn.execute(
            """
            SELECT
                b.latitude,
                b.longitude,
                b.status,
                bl.speed,
                bl.recorded_at
            FROM buses b
            JOIN students s ON s.bus_id = b.bus_id
            LEFT JOIN bus_locations bl
                ON bl.location_id = (
                    SELECT MAX(location_id)
                    FROM bus_locations
                    WHERE bus_id = b.bus_id
                )
            WHERE s.parent_id = ?
            ORDER BY s.student_id DESC
            LIMIT 1
            """,
            (session["user_id"],)
        ).fetchone()

        if location:
            return jsonify(dict(location))

        return jsonify({
            "latitude": None,
            "longitude": None,
            "status": "Waiting",
            "speed": 0
        })

    finally:
        conn.close()


# ---------------- DISTANCE AND ETA ----------------

def calculate_distance(lat1, lon1, lat2, lon2):
    radius = 6371.0

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    return 2 * radius * atan2(sqrt(a), sqrt(1 - a))


@app.route("/api/eta")
@login_required
def get_eta():
    try:
        target_lat = float(request.args["lat"])
        target_lon = float(request.args["lon"])
    except (KeyError, ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Provide stop coordinates using lat and lon."
        }), 400

    if not (-90 <= target_lat <= 90 and -180 <= target_lon <= 180):
        return jsonify({
            "success": False,
            "message": "Invalid stop coordinates."
        }), 400

    conn = get_connection()

    try:
        bus = conn.execute(
            """
            SELECT b.latitude, b.longitude
            FROM buses b
            JOIN students s ON s.bus_id = b.bus_id
            WHERE s.parent_id = ?
              AND b.latitude IS NOT NULL
              AND b.longitude IS NOT NULL
            ORDER BY s.student_id DESC
            LIMIT 1
            """,
            (session["user_id"],)
        ).fetchone()

        if not bus:
            return jsonify({
                "success": False,
                "message": "Bus location is not available."
            }), 404

        distance = calculate_distance(
            bus["latitude"],
            bus["longitude"],
            target_lat,
            target_lon
        )

        # Approximation only; this is not road-route navigation.
        eta_minutes = round(distance / 20 * 60)

        return jsonify({
            "success": True,
            "distance_km": round(distance, 2),
            "eta_minutes": eta_minutes
        })

    finally:
        conn.close()


# ---------------- NOTIFICATIONS ----------------

@app.route("/api/notifications")
@login_required
def get_notifications():
    conn = get_connection()

    try:
        bus = conn.execute(
            """
            SELECT b.bus_number, b.status, bl.recorded_at
            FROM buses b
            JOIN students s ON s.bus_id = b.bus_id
            LEFT JOIN bus_locations bl
                ON bl.location_id = (
                    SELECT MAX(location_id)
                    FROM bus_locations
                    WHERE bus_id = b.bus_id
                )
            WHERE s.parent_id = ?
            ORDER BY s.student_id DESC
            LIMIT 1
            """,
            (session["user_id"],)
        ).fetchone()

        messages = []

        if bus:
            messages.append({
                "message": "Bus " + str(bus["bus_number"])
                + " status: " + str(bus["status"] or "Waiting")
            })

            if bus["recorded_at"]:
                messages.append({
                    "message": "Last location update: "
                    + str(bus["recorded_at"])
                })
        else:
            messages.append({
                "message": "Add student and bus details to receive updates."
            })

        return jsonify({"notifications": messages})

    finally:
        conn.close()


# ---------------- DASHBOARD STATUS ----------------

@app.route("/api/status")
@login_required
def get_status():
    conn = get_connection()

    try:
        student_count = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM students
            WHERE parent_id = ?
            """,
            (session["user_id"],)
        ).fetchone()["total"]

        bus_count = conn.execute(
            """
            SELECT COUNT(DISTINCT bus_id) AS total
            FROM students
            WHERE parent_id = ? AND bus_id IS NOT NULL
            """,
            (session["user_id"],)
        ).fetchone()["total"]

        return jsonify({
            "success": True,
            "student_count": student_count,
            "bus_count": bus_count,
            "logged_in_as": session["name"]
        })

    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
