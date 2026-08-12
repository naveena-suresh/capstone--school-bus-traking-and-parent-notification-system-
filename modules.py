from database import get_connection


# ---------- USER ----------

def create_user(name, email, password, role):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO users (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (name, email, password, role))

    connection.commit()
    user_id = cursor.lastrowid
    connection.close()

    return user_id


def get_users():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users")
    users = [dict(row) for row in cursor.fetchall()]

    connection.close()
    return users


# ---------- BUS ----------

def create_bus(bus_number, driver_name, route_name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO buses
        (bus_number, driver_name, route_name)
        VALUES (?, ?, ?)
    """, (bus_number, driver_name, route_name))

    connection.commit()
    bus_id = cursor.lastrowid
    connection.close()

    return bus_id


def get_buses():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM buses")
    buses = [dict(row) for row in cursor.fetchall()]

    connection.close()
    return buses


def get_bus(bus_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM buses WHERE bus_id = ?",
        (bus_id,)
    )

    bus = cursor.fetchone()
    connection.close()

    return dict(bus) if bus else None


def update_bus_location(bus_id, latitude, longitude, speed=0, status=None):
    connection = get_connection()
    cursor = connection.cursor()

    if status:
        cursor.execute("""
            UPDATE buses
            SET latitude = ?, longitude = ?, status = ?
            WHERE bus_id = ?
        """, (latitude, longitude, status, bus_id))
    else:
        cursor.execute("""
            UPDATE buses
            SET latitude = ?, longitude = ?
            WHERE bus_id = ?
        """, (latitude, longitude, bus_id))

    cursor.execute("""
        INSERT INTO bus_locations
        (bus_id, latitude, longitude, speed)
        VALUES (?, ?, ?, ?)
    """, (bus_id, latitude, longitude, speed))

    connection.commit()
    connection.close()


# ---------- STUDENT ----------

def create_student(name, parent_id, bus_id, stop_name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO students
        (name, parent_id, bus_id, stop_name)
        VALUES (?, ?, ?, ?)
    """, (name, parent_id, bus_id, stop_name))

    connection.commit()
    student_id = cursor.lastrowid
    connection.close()

    return student_id


def get_students():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM students")
    students = [dict(row) for row in cursor.fetchall()]

    connection.close()
    return students


def get_student_bus(student_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            students.student_id,
            students.name AS student_name,
            students.stop_name,
            buses.bus_id,
            buses.bus_number,
            buses.driver_name,
            buses.route_name,
            buses.status,
            buses.latitude,
            buses.longitude
        FROM students
        LEFT JOIN buses
            ON students.bus_id = buses.bus_id
        WHERE students.student_id = ?
    """, (student_id,))

    result = cursor.fetchone()
    connection.close()

    return dict(result) if result else None


# ---------- ROUTE ----------

def create_route(route_name, start_point, end_point):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO routes
        (route_name, start_point, end_point)
        VALUES (?, ?, ?)
    """, (route_name, start_point, end_point))

    connection.commit()
    route_id = cursor.lastrowid
    connection.close()

    return route_id


def get_routes():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM routes")
    routes = [dict(row) for row in cursor.fetchall()]

    connection.close()
    return routes


# ---------- NOTIFICATION ----------

def create_notification(parent_id, message, notification_type):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO notifications
        (parent_id, message, notification_type)
        VALUES (?, ?, ?)
    """, (parent_id, message, notification_type))

    connection.commit()
    notification_id = cursor.lastrowid
    connection.close()

    return notification_id


def get_notifications(parent_id=None):
    connection = get_connection()
    cursor = connection.cursor()

    if parent_id:
        cursor.execute("""
            SELECT * FROM notifications
            WHERE parent_id = ?
            ORDER BY created_at DESC
        """, (parent_id,))
    else:
        cursor.execute("""
            SELECT * FROM notifications
            ORDER BY created_at DESC
        """)

    notifications = [dict(row) for row in cursor.fetchall()]

    connection.close()
    return notifications