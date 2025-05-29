from flask import Flask, jsonify, request, render_template, redirect, url_for, session
import mysql.connector
from mysql.connector import pooling
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'  # Required for session management

# Database configuration
db_config = {
    'user': 'root',
    'password': '',  
    'host': 'localhost',
    'database': 'eventshub',  
    'pool_name': 'eventshub_pool',
    'pool_size': 10,  # Number of connections in the pool
}

# Create a connection pool (initialized later after database creation)
connection_pool = None

# Function to create the database if it doesn't exist
def create_database():
    try:
        connection = mysql.connector.connect(
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host']
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS eventshub")
        print("Database created or already exists.")
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Function to create tables if they don't exist
def create_tables():
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        # Create users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL UNIQUE,
            password VARCHAR(200) NOT NULL,
            role ENUM('user', 'vendor') DEFAULT 'user'
        )
        """)

        # Create vendor_locations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendor_locations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            address VARCHAR(255) NOT NULL,
            country VARCHAR(100) NOT NULL,
            region VARCHAR(100),
            district VARCHAR(100),
            street_ward VARCHAR(100),
            vendor_id INT NOT NULL,  -- Track which vendor added the location
            FOREIGN KEY (vendor_id) REFERENCES users(id)
        )
        """)

        # Create vendor_venues table with a status column
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendor_venues (
            id INT AUTO_INCREMENT PRIMARY KEY,
            location_id INT NOT NULL,
            name VARCHAR(120) NOT NULL UNIQUE,
            description TEXT,
            capacity INT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            vendor_id INT NOT NULL,
            status ENUM('available', 'booked') DEFAULT 'available',  -- Track venue availability
            image_path VARCHAR(255),  -- Path to the venue image
            FOREIGN KEY (location_id) REFERENCES vendor_locations(id),
            FOREIGN KEY (vendor_id) REFERENCES users(id)
        )
        """)

        



        # Create vendor_services table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendor_services (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(120) NOT NULL UNIQUE,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL,
            vendor_id INT NOT NULL,  -- Track which vendor added the service
            FOREIGN KEY (vendor_id) REFERENCES users(id)
        )
        """)



        # Create vendor_events table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendor_events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(120) NOT NULL UNIQUE,
            description TEXT,
            date DATE NOT NULL,
            venue_id INT NOT NULL,
            service_id INT NOT NULL,
            vendor_id INT NOT NULL,  -- Track which vendor added the event
            image_path VARCHAR(255),
            FOREIGN KEY (venue_id) REFERENCES vendor_venues(id),
            FOREIGN KEY (service_id) REFERENCES vendor_services(id),
            FOREIGN KEY (vendor_id) REFERENCES users(id)
        )
        """)




        # Create admin_locations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_locations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            address VARCHAR(255) NOT NULL,
            country VARCHAR(100) NOT NULL,
            region VARCHAR(100),
            district VARCHAR(100),
            street_ward VARCHAR(100)
        )
        """)

        # Create admin_venues table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_venues (
            id INT AUTO_INCREMENT PRIMARY KEY,
            location_id INT NOT NULL,
            name VARCHAR(120) NOT NULL UNIQUE,
            description TEXT,
            capacity INT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            status ENUM('available', 'booked') DEFAULT 'available', 
            image_path VARCHAR(255),       
            FOREIGN KEY (location_id) REFERENCES admin_locations(id)
        )
        """)

 

        # Create admin_services table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_services (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(120) NOT NULL UNIQUE,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL
        )
        """)



        # Create admin_events table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(120) NOT NULL UNIQUE,
            description TEXT,
            date DATE NOT NULL,
            venue_id INT NOT NULL,
            service_id INT NOT NULL,
            image_path VARCHAR(255),
            FOREIGN KEY (venue_id) REFERENCES admin_venues(id),
            FOREIGN KEY (service_id) REFERENCES admin_services(id)
        )
        """)


        # Create bookings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            vendor_id INT NOT NULL,
            venue_id INT,
            service_id INT,
            booking_date DATE NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (vendor_id) REFERENCES users(id),
            FOREIGN KEY (venue_id) REFERENCES vendor_venues(id),
            FOREIGN KEY (service_id) REFERENCES vendor_services(id)
        )
        """)



        print("Tables created or already exist.")
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Initialize database and tables
create_database()

# Reinitialize the connection pool after the database is created
try:
    db_config['database'] = 'eventshub'  # Ensure the database name is set
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)
    print("Connection pool created successfully")
except mysql.connector.Error as err:
    print(f"Error: {err}")

create_tables()

# Hardcoded admin credentials (for demonstration purposes)
HARD_CODED_ADMIN = {
    'username': 'superadmin',
    'password': 'superpassword123'  # Use a hashed password in production
}

# Route for user registration
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data['username']
        email = data['email']
        password = data['password']
        role = data['role']  # Get the selected role (user or vendor)

        print(f"Registering user: {username}, Email: {email}, Role: {role}")  # Debug log

        # Hash the password
        hashed_password = generate_password_hash(password)

        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        # Insert user into the database with the selected role
        cursor.execute("""
        INSERT INTO users (username, email, password, role)
        VALUES (%s, %s, %s, %s)
        """, (username, email, hashed_password, role))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "User registered successfully!"}), 201
    except mysql.connector.Error as err:
        print(f"Database error: {err}")  # Debug log
        return jsonify({"error": str(err)}), 400

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data['username']
        password = data['password']

        print(f"Username: {username}, Password: {password}")  # Debug log

        # Check if the user is the hardcoded admin
        if username == HARD_CODED_ADMIN['username'] and password == HARD_CODED_ADMIN['password']:
            session['user_signed_in'] = True
            session['user_role'] = 'admin'  # Hardcoded admin role
            print("Admin login successful. Redirecting to admin dashboard.")  # Debug log
            return redirect(url_for('admin_dashboard'))

        # Check the database for regular users or vendors
        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user and check_password_hash(user['password'], password):
            session['user_signed_in'] = True
            session['user_role'] = user.get('role', 'user')  # Default to 'user' if no role is set
            session['user_id'] = user['id']  # Set user_id in session

            # Redirect based on role
            if session['user_role'] == 'vendor':
                print("Vendor login successful. Redirecting to vendor dashboard.")  # Debug log
                return redirect(url_for('vendor_dashboard'))
            else:
                print("User login successful. Redirecting to EventHub.")  # Debug log
                return redirect(url_for('eventhub'))
        else:
            print("Invalid username or password.")  # Debug log
            return jsonify({"error": "Invalid username or password"}), 401
    except mysql.connector.Error as err:
        print(f"Database error: {err}")  # Debug log
        return jsonify({"error": str(err)}), 400

@app.route('/logout')
def logout():
    session.pop('user_signed_in', None)  # Remove user_signed_in from session
    return redirect(url_for('eventhub'))  # Redirect to EventHub page

@app.route('/')
def eventhub():
    # Render EventHub.html by default
    user_signed_in = session.get('user_signed_in', False)
    return render_template('EventHub.html', user_signed_in=user_signed_in)

@app.route('/userdashboard')
def user_dashboard():
    user_signed_in = session.get('user_signed_in', False)
    if not user_signed_in:
        return redirect(url_for('eventhub'))  # Redirect to login if not signed in
    return render_template('Userdashboard.html', user_signed_in=user_signed_in)


@app.route('/venues')
def venues():
    user_signed_in = session.get('user_signed_in', False)
    return render_template('venues.html', user_signed_in=user_signed_in)

@app.route('/events')
def events():
    user_signed_in = session.get('user_signed_in', False)
    return render_template('Events.html', user_signed_in=user_signed_in)

@app.route('/booking')
def booking():
    return render_template('booking.html')

# Route for about page
@app.route('/about')
def about():
    user_signed_in = session.get('user_signed_in', False)
    return render_template('about.html', user_signed_in=user_signed_in)

# Route for contact page
@app.route('/contact')
def contact():
    user_signed_in = session.get('user_signed_in', False)
    return render_template('Contact.html', user_signed_in=user_signed_in)

@app.route('/index')
def index():
    form_type = request.args.get('form', 'login')  # Default to 'login' if no form type is specified
    return render_template('index.html', form=form_type)

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('user_signed_in') or session.get('user_role') != 'admin':
        return redirect(url_for('eventhub'))  # Redirect if unauthorized

    connection = connection_pool.get_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch total members (users)
    cursor.execute("SELECT COUNT(*) AS total_users FROM users WHERE role = 'user'")
    total_users = cursor.fetchone()['total_users']

    # Fetch all vendors
    cursor.execute("SELECT COUNT(*) AS total_vendors FROM users WHERE role = 'vendor'")
    total_vendors = cursor.fetchone()['total_vendors']

    # Fetch available venues (both vendor and admin added)
    cursor.execute("""
        SELECT COUNT(*) AS available_venues 
        FROM vendor_venues 
        WHERE status = 'available'
        UNION ALL
        SELECT COUNT(*) AS available_venues 
        FROM admin_venues 
        WHERE status = 'available'
    """)
    available_venues = sum([row['available_venues'] for row in cursor.fetchall()])

    # Fetch booked venues (both vendor and admin added)
    cursor.execute("""
        SELECT COUNT(*) AS booked_venues 
        FROM vendor_venues 
        WHERE status = 'booked'
        UNION ALL
        SELECT COUNT(*) AS booked_venues 
        FROM admin_venues 
        WHERE status = 'booked'
    """)
    booked_venues = sum([row['booked_venues'] for row in cursor.fetchall()])

    # Fetch total services (both vendor and admin added)
    cursor.execute("""
        SELECT COUNT(*) AS total_services 
        FROM vendor_services
        UNION ALL
        SELECT COUNT(*) AS total_services 
        FROM admin_services
    """)
    total_services = sum([row['total_services'] for row in cursor.fetchall()])

    # Fetch all locations (vendor and admin added)
    cursor.execute("""
        SELECT id, address, country, region, district, street_ward, 'vendor' AS source
        FROM vendor_locations
        UNION ALL
        SELECT id, address, country, region, district, street_ward, 'admin' AS source
        FROM admin_locations
    """)
    all_locations = cursor.fetchall()

    # Fetch all venues (vendor and admin added)
    cursor.execute("""
        SELECT id, location_id, name, description, capacity, price, status, 'vendor' AS source
        FROM vendor_venues
        UNION ALL
        SELECT id, location_id, name, description, capacity, price, status, 'admin' AS source
        FROM admin_venues
    """)
    all_venues = cursor.fetchall()

    # Fetch all services (vendor and admin added)
    cursor.execute("""
        SELECT id, name, description, price, 'vendor' AS source
        FROM vendor_services
        UNION ALL
        SELECT id, name, description, price, 'admin' AS source
        FROM admin_services
    """)
    all_services = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_vendors=total_vendors,
        available_venues=available_venues,
        booked_venues=booked_venues,
        total_services=total_services,
        all_locations=all_locations,
        all_venues=all_venues,
        all_services=all_services
    )

@app.route('/vendor', methods=['GET', 'POST'])
def vendor_dashboard():
    if not session.get('user_signed_in') or session.get('user_role') != 'vendor':
        return redirect(url_for('eventhub'))  # Redirect if unauthorized

    vendor_id = session['user_id']  # Get the logged-in vendor's ID

    connection = connection_pool.get_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch vendor-specific locations
    cursor.execute("SELECT * FROM vendor_locations WHERE vendor_id = %s", (vendor_id,))
    vendor_locations = cursor.fetchall()

    # Fetch vendor-specific venues
    cursor.execute("SELECT * FROM vendor_venues WHERE vendor_id = %s", (vendor_id,))
    vendor_venues = cursor.fetchall()

    # Fetch vendor-specific services
    cursor.execute("SELECT * FROM vendor_services WHERE vendor_id = %s", (vendor_id,))
    vendor_services = cursor.fetchall()

    # Calculate metrics for the vendor
    cursor.execute("SELECT COUNT(*) AS total_services FROM vendor_services WHERE vendor_id = %s", (vendor_id,))
    total_services = cursor.fetchone()['total_services']

    cursor.execute("SELECT COUNT(*) AS total_venues FROM vendor_venues WHERE vendor_id = %s", (vendor_id,))
    total_venues = cursor.fetchone()['total_venues']

    cursor.execute("SELECT COUNT(*) AS available_venues FROM vendor_venues WHERE vendor_id = %s AND status = 'available'", (vendor_id,))
    available_venues = cursor.fetchone()['available_venues']

    cursor.execute("SELECT COUNT(*) AS booked_venues FROM vendor_venues WHERE vendor_id = %s AND status = 'booked'", (vendor_id,))
    booked_venues = cursor.fetchone()['booked_venues']

    cursor.execute("SELECT COUNT(*) AS total_bookings FROM bookings WHERE vendor_id = %s", (vendor_id,))
    total_bookings = cursor.fetchone()['total_bookings']

    cursor.execute("SELECT COUNT(*) AS booked_services FROM bookings WHERE vendor_id = %s AND service_id IS NOT NULL", (vendor_id,))
    booked_services = cursor.fetchone()['booked_services']

    cursor.close()
    connection.close()

    return render_template(
        'vendor_dashboard.html',
        vendor_locations=vendor_locations,
        vendor_venues=vendor_venues,
        vendor_services=vendor_services,
        total_services=total_services,
        total_venues=total_venues,
        available_venues=available_venues,
        booked_venues=booked_venues,
        total_bookings=total_bookings,
        booked_services=booked_services
    )

@app.route('/add_location', methods=['POST'])
def add_location():
    if not session.get('user_signed_in') or session.get('user_role') not in ['admin', 'vendor']:
        return jsonify({"success": False, "error": "Unauthorized access"}), 403

    try:
        data = request.form
        address = data['address']
        country = data['country']
        region = data.get('region', None)
        district = data.get('district', None)
        street_ward = data.get('street_ward', None)
        added_by_role = session.get('user_role')  # Get the role of the logged-in user

        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        if added_by_role == 'vendor':
            vendor_id = session.get('user_id')  # Use the logged-in vendor's ID

            # Verify that the vendor exists in the users table
            cursor.execute("SELECT * FROM users WHERE id = %s AND role = 'vendor'", (vendor_id,))
            user = cursor.fetchone()

            if not user:
                cursor.close()
                connection.close()
                return jsonify({"success": False, "error": "Vendor does not exist or is not authorized"}), 400

            # Insert into vendor_locations table
            cursor.execute("""
                INSERT INTO vendor_locations (address, country, region, district, street_ward, vendor_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (address, country, region, district, street_ward, vendor_id))

        elif added_by_role == 'admin':
            # Insert into admin_locations table
            cursor.execute("""
                INSERT INTO admin_locations (address, country, region, district, street_ward)
                VALUES (%s, %s, %s, %s, %s)
            """, (address, country, region, district, street_ward))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": True})  # Return success response
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({"success": False, "error": str(err)}), 500


@app.route('/add_venue', methods=['POST'])
def add_venue():
    if not session.get('user_signed_in') or session.get('user_role') not in ['admin', 'vendor']:
        return jsonify({"success": False, "error": "Unauthorized access"}), 403

    try:
        data = request.form
        venue_name = data['venue_name']
        venue_description = data.get('venue_description', None)
        venue_capacity = data['venue_capacity']
        venue_price = data['venue_price']
        location_id = data['location_id']
        added_by_role = session.get('user_role')  # Get the role of the logged-in user
        venue_image = request.files['venue_image']  # Get the uploaded image

        # Determine the folder based on the role
        if added_by_role == 'vendor':
            vendor_id = session.get('user_id')  # Use the logged-in vendor's ID
            image_folder = 'static/venue_images'
            image_path = f"{image_folder}/{venue_image.filename}"
        elif added_by_role == 'admin':
            image_folder = 'static/admin_venue_images'
            image_path = f"{image_folder}/{venue_image.filename}"

        # Save the image to the appropriate folder
        venue_image.save(image_path)

        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        # Check for duplicate venue names
        if added_by_role == 'vendor':
            cursor.execute("SELECT * FROM vendor_venues WHERE name = %s AND vendor_id = %s", (venue_name, vendor_id))
            existing_venue = cursor.fetchone()
        elif added_by_role == 'admin':
            cursor.execute("SELECT * FROM admin_venues WHERE name = %s", (venue_name,))
            existing_venue = cursor.fetchone()

        if existing_venue:
            cursor.close()
            connection.close()
            return jsonify({"success": False, "error": "Venue name already exists"}), 400

        # Insert new venue
        if added_by_role == 'vendor':
            cursor.execute("""
                INSERT INTO vendor_venues (name, description, capacity, price, location_id, vendor_id, image_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (venue_name, venue_description, venue_capacity, venue_price, location_id, vendor_id, image_path))
        elif added_by_role == 'admin':
            cursor.execute("""
                INSERT INTO admin_venues (name, description, capacity, price, location_id, image_path)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (venue_name, venue_description, venue_capacity, venue_price, location_id, image_path))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": True})  # Return success response
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/add_service', methods=['POST'])
def add_service():
    if not session.get('user_signed_in') or session.get('user_role') not in ['admin', 'vendor']:
        return jsonify({"success": False, "error": "Unauthorized access"}), 403

    try:
        data = request.form
        service_name = data['service_name']
        service_description = data.get('service_description', None)
        service_price = data['service_price']
        added_by_role = session.get('user_role')  # Get the role of the logged-in user

        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        if added_by_role == 'vendor':
            vendor_id = session.get('user_id')  # Use the logged-in vendor's ID

            # Verify that the vendor exists in the users table
            cursor.execute("SELECT * FROM users WHERE id = %s AND role = 'vendor'", (vendor_id,))
            user = cursor.fetchone()

            if not user:
                cursor.close()
                connection.close()
                return jsonify({"success": False, "error": "Vendor does not exist or is not authorized"}), 400

            # Insert into vendor_services table
            cursor.execute("""
                INSERT INTO vendor_services (name, description, price, vendor_id)
                VALUES (%s, %s, %s, %s)
            """, (service_name, service_description, service_price, vendor_id))

        elif added_by_role == 'admin':
            # Insert into admin_services table
            cursor.execute("""
                INSERT INTO admin_services (name, description, price)
                VALUES (%s, %s, %s)
            """, (service_name, service_description, service_price))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": True})  # Return success response
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({"success": False, "error": str(err)}), 500


@app.route('/add_event', methods=['POST'])
def add_event():
    if not session.get('user_signed_in') or session.get('user_role') not in ['admin', 'vendor']:
        return jsonify({"success": False, "error": "Unauthorized access"}), 403

    try:
        data = request.form
        event_name = data['event_name']
        event_description = data.get('event_description', None)
        event_date = data['event_date']
        event_venue_id = data['event_venue_id']
        event_service_id = data.get('event_service_id', None)
        added_by_role = session.get('user_role')  # Get the role of the logged-in user
        event_image = request.files['event_image']  # Get the uploaded image

        # Determine the folder based on the role
        if added_by_role == 'vendor':
            vendor_id = session.get('user_id')  # Use the logged-in vendor's ID
            image_folder = 'static/event_images'
            image_path = f"{image_folder}/{event_image.filename}"
        elif added_by_role == 'admin':
            image_folder = 'static/admin_event_images'
            image_path = f"{image_folder}/{event_image.filename}"

        # Save the image to the appropriate folder
        event_image.save(image_path)

        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        if added_by_role == 'vendor':
            vendor_id = session.get('user_id')  # Use the logged-in vendor's ID

            # Verify that the vendor exists in the users table
            cursor.execute("SELECT * FROM users WHERE id = %s AND role = 'vendor'", (vendor_id,))
            user = cursor.fetchone()

            if not user:
                cursor.close()
                connection.close()
                return jsonify({"success": False, "error": "Vendor does not exist or is not authorized"}), 400

            # Insert into vendor_events table
            cursor.execute("""
                INSERT INTO vendor_events (name, description, date, venue_id, service_id, vendor_id, image_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (event_name, event_description, event_date, event_venue_id, event_service_id, vendor_id, image_path))

        elif added_by_role == 'admin':
            # Insert into admin_events table
            cursor.execute("""
                INSERT INTO admin_events (name, description, date, venue_id, service_id, image_path)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (event_name, event_description, event_date, event_venue_id, event_service_id, image_path))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": True})  # Return success response
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/metrics', methods=['GET'])
def get_metrics():
    if not session.get('user_signed_in') or session.get('user_role') not in ['admin', 'vendor']:
        return redirect(url_for('eventhub'))  # Redirect if unauthorized

    connection = connection_pool.get_connection()
    cursor = connection.cursor(dictionary=True)

    # Metrics for both admin and vendor
    cursor.execute("SELECT COUNT(*) AS total_services FROM services")
    total_services = cursor.fetchone()['total_services']

    cursor.execute("SELECT COUNT(*) AS booked_services FROM bookings")
    booked_services = cursor.fetchone()['booked_services']

    cursor.execute("SELECT COUNT(*) AS total_bookings FROM bookings")
    total_bookings = cursor.fetchone()['total_bookings']

    cursor.execute("SELECT COUNT(*) AS available_venues FROM venues WHERE status = 'available'")
    available_venues = cursor.fetchone()['available_venues']

    cursor.execute("SELECT COUNT(*) AS booked_venues FROM venues WHERE status = 'booked'")
    booked_venues = cursor.fetchone()['booked_venues']

    cursor.close()
    connection.close()

    return jsonify({
        "total_services": total_services,
        "booked_services": booked_services,
        "total_bookings": total_bookings,
        "available_venues": available_venues,
        "booked_venues": booked_venues
    })

@app.route('/get_locations', methods=['GET'])
def get_locations():
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        user_role = session.get('user_role')
        user_id = session.get('user_id')

        if user_role == 'vendor':
            # Fetch locations added by the vendor
            cursor.execute("""
                SELECT id, address, country, region, district, street_ward 
                FROM vendor_locations 
                WHERE vendor_id = %s
            """, (user_id,))
        elif user_role == 'admin':
            # Fetch all locations added by admin
            cursor.execute("""
                SELECT id, address, country, region, district, street_ward 
                FROM admin_locations
            """)
        else:
            return jsonify({'error': 'Unauthorized access'}), 403

        locations = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({'locations': locations})
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({'error': 'Failed to fetch locations'}), 500


@app.route('/get_venues_and_services', methods=['GET'])
def get_venues_and_services():
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        user_role = session.get('user_role')
        user_id = session.get('user_id')

        if user_role == 'vendor':
            # Fetch venues and services added by the vendor
            cursor.execute("SELECT id, name FROM vendor_venues WHERE vendor_id = %s", (user_id,))
            venues = cursor.fetchall()

            cursor.execute("SELECT id, name FROM vendor_services WHERE vendor_id = %s", (user_id,))
            services = cursor.fetchall()
        elif user_role == 'admin':
            # Fetch all venues and services added by admin
            cursor.execute("SELECT id, name FROM admin_venues")
            venues = cursor.fetchall()

            cursor.execute("SELECT id, name FROM admin_services")
            services = cursor.fetchall()
        else:
            return jsonify({'error': 'Unauthorized access'}), 403

        cursor.close()
        connection.close()

        return jsonify({'venues': venues, 'services': services})
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({'error': 'Failed to fetch venues and services'}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
