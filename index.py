from flask import Flask, jsonify, request, send_from_directory
from database import get_connection, initialize_database

app = Flask(__name__)


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


# =========================
# SAVE STUDENT DETAILS
# =========================

@app.route("/api/save-details", methods=["POST"])
def save_details():

    try:
        data = request.get_json()

        student = data.get("student", "")
        student_id = data.get("studentId", "")
        parent = data.get("parent", "")
        phone = data.get("phone", "")
        bus = data.get("bus", "")
        driver = data.get("driver", "")
        location = data.get("location", "")
        route = data.get("route", "")

        connection = get_connection()
        cursor = connection.cursor()

        email = phone + "@school.com"

        cursor.execute("""
            INSERT OR IGNORE INTO users
            (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (
            parent,
            email,
            "1234",
            "parent"
        ))

        cursor.execute("""
            SELECT user_id
            FROM users
            WHERE email = ?
        """, (email,))

        parent_row = cursor.fetchone()

        if not parent_row:
            connection.close()
            return jsonify({
                "success": False,
                "message": "Parent could not be created"
            }), 500

        parent_id = parent_row["user_id"]

        cursor.execute("""
            INSERT OR IGNORE INTO buses
            (bus_number, driver_name, route_name, status)
            VALUES (?, ?, ?, ?)
        """, (
            bus,
            driver,
            route,
            "Running"
        ))

        cursor.execute("""
            SELECT bus_id
            FROM buses
            WHERE bus_number = ?
        """, (bus,))

        bus_row = cursor.fetchone()

        if not bus_row:
            connection.close()
            return jsonify({
                "success": False,
                "message": "Bus could not be created"
            }), 500

        bus_id = bus_row["bus_id"]

        cursor.execute("""
            INSERT INTO students
            (name, parent_id, bus_id, stop_name)
            VALUES (?, ?, ?, ?)
        """, (
            student,
            parent_id,
            bus_id,
            location
        ))

        connection.commit()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Details saved successfully!",
            "student": student,
            "studentId": student_id,
            "parent": parent,
            "phone": phone,
            "bus": bus,
            "driver": driver,
            "location": location,
            "route": route
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# =========================
# GET STUDENT DETAILS
# =========================

@app.route("/api/student")
def get_student():

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                students.name AS student,
                students.student_id AS studentId,
                users.name AS parent,
                buses.bus_number AS bus,
                buses.driver_name AS driver,
                students.stop_name AS location,
                buses.route_name AS route
            FROM students
            LEFT JOIN users
                ON students.parent_id = users.user_id
            LEFT JOIN buses
                ON students.bus_id = buses.bus_id
            ORDER BY students.student_id DESC
            LIMIT 1
        """)

        row = cursor.fetchone()
        connection.close()

        if row:
            return jsonify(dict(row))

        return jsonify({
            "student": "Not Added",
            "studentId": "Not Added",
            "parent": "Not Added",
            "phone": "Not Added",
            "bus": "Not Added",
            "driver": "Not Added",
            "location": "Not Added",
            "route": "Not Added"
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# =========================
# BUS DETAILS
# =========================

@app.route("/api/bus")
def get_bus():

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                bus_id,
                bus_number,
                driver_name,
                route_name,
                status,
                latitude,
                longitude
            FROM buses
            ORDER BY bus_id DESC
            LIMIT 1
        """)

        row = cursor.fetchone()
        connection.close()

        if row:
            return jsonify(dict(row))

        return jsonify({
            "bus_id": 0,
            "bus_number": "Not Added",
            "driver_name": "Not Added",
            "route_name": "Not Added",
            "status": "Stopped",
            "latitude": 0,
            "longitude": 0
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# =========================
# UPDATE BUS LOCATION
# =========================

@app.route("/api/update-location", methods=["POST"])
def update_location():

    try:
        data = request.get_json()

        latitude = data.get("latitude")
        longitude = data.get("longitude")
        speed = data.get("speed", 0)

        if latitude is None or longitude is None:
            return jsonify({
                "success": False,
                "message": "Latitude and longitude are required."
            }), 400

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT bus_id
            FROM buses
            ORDER BY bus_id DESC
            LIMIT 1
        """)

        bus = cursor.fetchone()

        if not bus:
            connection.close()

            return jsonify({
                "success": False,
                "message": "No bus found. Add a bus first."
            }), 404

        bus_id = bus["bus_id"]

        cursor.execute("""
            UPDATE buses
            SET latitude = ?,
                longitude = ?,
                status = ?
            WHERE bus_id = ?
        """, (
            latitude,
            longitude,
            "Running",
            bus_id
        ))

        connection.commit()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Bus location updated successfully!",
            "latitude": latitude,
            "longitude": longitude,
            "speed": speed
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# =========================
# LIVE LOCATION
# =========================

@app.route("/api/location")
def get_location():

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                latitude,
                longitude,
                status
            FROM buses
            ORDER BY bus_id DESC
            LIMIT 1
        """)

        row = cursor.fetchone()
        connection.close()

        if row:
            return jsonify({
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "speed": 0,
                "status": row["status"]
            })

        return jsonify({
            "latitude": 0,
            "longitude": 0,
            "speed": 0,
            "status": "No location data"
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# =========================
# ETA
# =========================

@app.route("/api/eta")
def get_eta():

    return jsonify({
        "eta": "10 minutes",
        "message": "Estimated arrival time"
    })


# =========================
# NOTIFICATIONS
# =========================

@app.route("/api/notifications")
def get_notifications():

    return jsonify([
        {
            "message": "Bus has started from school."
        },
        {
            "message": "Bus is currently on the route."
        },
        {
            "message": "Estimated arrival time is 10 minutes."
        }
    ])


# =========================
# SYSTEM STATUS
# =========================

@app.route("/api/status")
def get_status():

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM buses
        """)

        total_buses = cursor.fetchone()["count"]

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM students
        """)

        total_students = cursor.fetchone()["count"]

        connection.close()

        return jsonify({
            "message": "School Bus Tracking System API",
            "status": "Online",
            "totalBuses": total_buses,
            "totalStudents": total_students
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":

    initialize_database()

    print("=" * 50)
    print("School Bus Tracking System")
    print("=" * 50)
    print("Server starting...")
    print("Open: http://127.0.0.1:5000")
    print("=" * 50)

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )