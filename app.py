from flask import Flask, jsonify, request, render_template, redirect, url_for, session
import mysql.connector
from mysql.connector import pooling
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import Markup

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'  # Required for session management

# Database configuration
db_config = {
    'user': 'root',
    'password': '',  
    'host': 'localhost',
    'database': 'eventshub',  
    'pool_name': 'eventshub_pool',
    'pool_size': 20,  # Number of connections in the pool
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
            role ENUM('user', 'vendor') DEFAULT 'user',
            wallet_balance DECIMAL(10, 2) DEFAULT 0
        )
        """)

        # Create admin table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_wallet (
            id INT AUTO_INCREMENT PRIMARY KEY,
            balance DECIMAL(10, 2) DEFAULT 0
        )
        """)
        cursor.execute("INSERT IGNORE INTO admin_wallet (balance) VALUES (0)")


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



        # Create admin_bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                venue_id INT NOT NULL,
                service_id VARCHAR(255),
                booking_date DATE NOT NULL,
                event VARCHAR(120) NOT NULL,
                service_amount DECIMAL(10, 2) NOT NULL,
                venue_amount DECIMAL(10, 2) NOT NULL,
                total_cost DECIMAL(10, 2) NOT NULL,
                payment_method VARCHAR(50) NOT NULL,
                location VARCHAR(255) NOT NULL,
                payment_status ENUM('Paid', 'Unpaid', 'Pending') DEFAULT 'Pending',
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (venue_id) REFERENCES admin_venues(id)
            )
        """)


        # Create vendor_bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendor_bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                vendor_id INT NOT NULL,
                venue_id INT NOT NULL,
                service_id VARCHAR(255),
                booking_date DATE NOT NULL,
                event VARCHAR(120) NOT NULL,
                service_amount DECIMAL(10, 2) NOT NULL,
                venue_amount DECIMAL(10, 2) NOT NULL,
                total_cost DECIMAL(10, 2) NOT NULL,
                payment_method VARCHAR(50) NOT NULL,
                location VARCHAR(255) NOT NULL,
                payment_status ENUM('Paid', 'Unpaid', 'Pending') DEFAULT 'Pending',
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (vendor_id) REFERENCES users(id),
                FOREIGN KEY (venue_id) REFERENCES vendor_venues(id)
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
        role = data.get('role', 'user')  # Default to 'user' if no role is provided

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

def get_unique_bookings(bookings):
    seen = set()
    unique = []
    for b in bookings:
        # Choose key fields that uniquely identify a booking
        key = (b['date'], b['venue'], b['location'], b['event'], b['status'])
        if key not in seen:
            seen.add(key)
            unique.append(b)
    return unique



@app.route('/userdashboard', methods=['GET'])
def user_dashboard():
    if not session.get('user_signed_in'):
        return redirect(url_for('eventhub'))  # Redirect to login if not signed in

    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch bookings from both admin_bookings and vendor_bookings
        cursor.execute("""
            SELECT b.id, b.booking_date, b.event, b.service_amount, b.venue_amount, b.total_cost, 
                b.payment_method, b.payment_status, b.location, u.username AS user_name, 
                v.name AS venue_name, v.image_path, b.service_id
            FROM vendor_bookings b
            LEFT JOIN users u ON b.user_id = u.id
            LEFT JOIN vendor_venues v ON b.venue_id = v.id
            WHERE b.user_id = %s
            UNION
            SELECT b.id, b.booking_date, b.event, b.service_amount, b.venue_amount, b.total_cost, 
                b.payment_method, b.payment_status, b.location, u.username AS user_name, 
                a.name AS venue_name, a.image_path, b.service_id
            FROM admin_bookings b
            LEFT JOIN users u ON b.user_id = u.id
            LEFT JOIN admin_venues a ON b.venue_id = a.id
            WHERE b.user_id = %s
        """, (session.get('user_id'), session.get('user_id')))
        booked_venues = cursor.fetchall()

        # Process services to make them readable
        for venue in booked_venues:
            if venue['service_id']:
                venue['services'] = venue['service_id']  # Directly use the service_id as services
            else:
                venue['services'] = 'No services selected'

        # Calculate total bookings and total payment
        total_bookings = len(booked_venues)
        total_payment = sum(venue['total_cost'] for venue in booked_venues)

        print(f"Booked venues: {booked_venues}")  # Debug log

        cursor.close()
        connection.close()

        return render_template('Userdashboard.html', user_signed_in=True, booked_venues=booked_venues, total_bookings=total_bookings, total_payment=total_payment)
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({'error': 'Failed to fetch booked venues'}), 500

@app.route('/venues', methods=['GET'])
def venues():
    try:
        user_signed_in = session.get('user_signed_in', False)

        update_venue_status()  # Update venue statuses dynamically based on the bookings table

        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch only available venues from both vendor and admin tables
        cursor.execute("""
            SELECT name, description, capacity, price, image_path
            FROM vendor_venues
            WHERE status = 'available'
            UNION
            SELECT name, description, capacity, price, image_path
            FROM admin_venues
            WHERE status = 'available'
        """)
        venues = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('venues.html', user_signed_in=user_signed_in, venues=venues)
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({"success": False, "error": str(err)}), 500
    

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

    # Update venue statuses dynamically based on the bookings table
    update_venue_status()

    connection = connection_pool.get_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch wallet balance for admin
    wallet_balance = calculate_wallet_balance(None, 'admin')

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

    # Fetch data for the chart (most booked venues and services)
    cursor.execute("""
        SELECT name AS label, COUNT(*) AS count
        FROM (
            -- Booked venues from admin
            SELECT v.name, b.venue_id FROM admin_venues v
            JOIN admin_bookings b ON v.id = b.venue_id
            UNION ALL
            -- Booked venues from vendors
            SELECT v.name, b.venue_id FROM vendor_venues v
            JOIN vendor_bookings b ON v.id = b.venue_id
            UNION ALL
            -- Booked services from admin
            SELECT s.name, b.service_id FROM admin_services s
            JOIN admin_bookings b ON FIND_IN_SET(s.id, b.service_id)
            UNION ALL
            -- Booked services from vendors
            SELECT s.name, b.service_id FROM vendor_services s
            JOIN vendor_bookings b ON FIND_IN_SET(s.id, b.service_id)
        ) AS combined
        GROUP BY label
        ORDER BY count DESC
        LIMIT 10
    """)
    chart_data = cursor.fetchall()
    chart_labels = [item['label'] for item in chart_data]
    chart_counts = [item['count'] for item in chart_data]

    # Fetch recent bookings
    cursor.execute("""
        SELECT * FROM (
            SELECT b.booking_date, b.event, b.location, u.username, v.name AS venue_name, NULL AS vendor_name
            FROM admin_bookings b
            LEFT JOIN users u ON b.user_id = u.id
            LEFT JOIN admin_venues v ON b.venue_id = v.id
            UNION ALL
            SELECT b.booking_date, b.event, b.location, u.username, v.name AS venue_name, u2.username AS vendor_name
            FROM vendor_bookings b
            LEFT JOIN users u ON b.user_id = u.id
            LEFT JOIN vendor_venues v ON b.venue_id = v.id
            LEFT JOIN users u2 ON b.vendor_id = u2.id
        ) AS combined_bookings
        ORDER BY booking_date DESC
        LIMIT 5
    """)
    recent_bookings = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_vendors=total_vendors,
        available_venues=available_venues,
        all_locations=all_locations,
        all_venues=all_venues,
        all_services=all_services,
        booked_venues=booked_venues,
        total_services=total_services,
        recent_bookings=recent_bookings,
        chart_labels=chart_labels,
        chart_data=chart_counts,
        wallet_balance=wallet_balance
    )


@app.route('/vendor', methods=['GET', 'POST'])
def vendor_dashboard():
    if not session.get('user_signed_in') or session.get('user_role') != 'vendor':
        return redirect(url_for('eventhub'))  # Redirect if unauthorized

    update_venue_status()  # Update venue statuses dynamically based on the bookings table

    vendor_id = session['user_id']  # Get the logged-in vendor's ID

    # Fetch wallet balance for vendor
    wallet_balance = calculate_wallet_balance(vendor_id, 'vendor')

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

    # Calculate total bookings for the vendor
    cursor.execute("SELECT COUNT(*) AS total_bookings FROM vendor_bookings WHERE vendor_id = %s", (vendor_id,))
    total_bookings = cursor.fetchone()['total_bookings']

    # Calculate booked services for the vendor
    cursor.execute("""
        SELECT COUNT(*) AS booked_services 
        FROM vendor_bookings 
        WHERE vendor_id = %s AND service_id IS NOT NULL
    """, (vendor_id,))
    booked_services = cursor.fetchone()['booked_services']


    # Fetch data for the chart (most booked venues and services for the vendor)
    cursor.execute("""
        SELECT name AS label, COUNT(*) AS count
        FROM (
            -- Booked venues
            SELECT v.name, b.venue_id FROM vendor_venues v
            JOIN vendor_bookings b ON v.id = b.venue_id
            WHERE v.vendor_id = %s
            UNION ALL
            -- Booked services
            SELECT s.name, b.service_id FROM vendor_services s
            JOIN vendor_bookings b ON FIND_IN_SET(s.id, b.service_id)
            WHERE s.vendor_id = %s
        ) AS combined
        GROUP BY label
        ORDER BY count DESC
        LIMIT 10
    """, (vendor_id, vendor_id))
    chart_data = cursor.fetchall()
    chart_labels = [item['label'] for item in chart_data]
    chart_counts = [item['count'] for item in chart_data]

# Fetch recent bookings based on booked services added by vendors
    cursor.execute("""
        SELECT b.booking_date, b.event, b.location, v.name AS venue_name, 
            GROUP_CONCAT(s.name SEPARATOR ', ') AS service_name
        FROM vendor_bookings b
        LEFT JOIN vendor_venues v ON b.venue_id = v.id
        LEFT JOIN vendor_services s ON FIND_IN_SET(s.id, b.service_id)
        WHERE b.vendor_id = %s
        GROUP BY b.id
        ORDER BY b.booking_date DESC
        LIMIT 5
    """, (vendor_id,))
    recent_bookings = cursor.fetchall()

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
        booked_services=booked_services,
        recent_bookings=recent_bookings,
        chart_labels=chart_labels,
        chart_data=chart_counts,
        wallet_balance=wallet_balance
    )


def calculate_wallet_balance(user_id, user_role):
    """Calculate the wallet balance for the logged-in user."""
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        # Initialize default values
        venue_income = 0
        service_income = 0

        if user_role == 'vendor':
            # Calculate wallet balance for vendor
            cursor.execute("""
                SELECT 
                    SUM(CASE 
                        WHEN b.vendor_id IS NOT NULL THEN b.venue_amount * 0.65 
                        ELSE 0 
                    END) AS venue_income,
                    SUM(CASE 
                        WHEN FIND_IN_SET(s.id, b.service_id) THEN s.price * 0.65 
                        ELSE 0 
                    END) AS service_income
                FROM vendor_bookings b
                LEFT JOIN vendor_services s ON FIND_IN_SET(s.id, b.service_id)
                WHERE b.vendor_id = %s
            """, (user_id,))
            result = cursor.fetchone()
            if result:
                venue_income = result['venue_income'] or 0
                service_income = result['service_income'] or 0

        elif user_role == 'admin':
            # Calculate wallet balance for admin
            cursor.execute("""
                SELECT 
                    SUM(venue_amount) AS venue_income,
                    SUM(service_amount) AS service_income
                FROM admin_bookings
            """)
            result = cursor.fetchone()
            if result:
                venue_income = result['venue_income'] or 0
                service_income = result['service_income'] or 0

            # Add 35% of vendor bookings to admin wallet
            cursor.execute("""
                SELECT 
                    SUM(b.venue_amount * 0.35) AS vendor_venue_income,
                    SUM(s.price * 0.35) AS vendor_service_income
                FROM vendor_bookings b
                LEFT JOIN vendor_services s ON FIND_IN_SET(s.id, b.service_id)
                WHERE b.vendor_id IS NOT NULL
            """)
            vendor_result = cursor.fetchone()
            if vendor_result:
                venue_income += vendor_result['vendor_venue_income'] or 0
                service_income += vendor_result['vendor_service_income'] or 0

        # Calculate total wallet balance
        wallet_balance = venue_income + service_income

        cursor.close()
        connection.close()
        return wallet_balance
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return 0

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
        elif added_by_role == 'admin':
            image_folder = 'static/admin_venue_images'

        # Save the image to the appropriate folder
        image_path = f"{image_folder}/{venue_image.filename}"
        venue_image.save(image_path)  # Save the image in the static folder

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

        # Fetch all locations from vendor_locations and admin_locations
        cursor.execute("""
            SELECT id, address, country, region, district, street_ward 
            FROM vendor_locations
            UNION
            SELECT id, address, country, region, district, street_ward 
            FROM admin_locations
        """)
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

@app.route('/filter_venues', methods=['GET'])
def filter_venues():

    
    try:
        capacity = request.args.get('capacity', None)  # Get selected capacity
        location_id = request.args.get('location_id', None)  # Get selected location ID
        search_term = request.args.get('search_term', None)  # Get search term

        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        # Base queries with filters applied individually
        vendor_query = """
            SELECT v.name, v.description, v.capacity, v.price, v.image_path, 
                   l.country, l.region, l.district, l.street_ward
            FROM vendor_venues v
            JOIN vendor_locations l ON v.location_id = l.id
            WHERE v.status = 'available'  -- Only fetch available venues
        """
        admin_query = """
            SELECT a.name, a.description, a.capacity, a.price, a.image_path, 
                   l.country, l.region, l.district, l.street_ward
            FROM admin_venues a
            JOIN admin_locations l ON a.location_id = l.id
            WHERE a.status = 'available'  -- Only fetch available venues
        """

        # Add filters to vendor query
        vendor_filters = []
        if capacity:
            if capacity == 'small':
                vendor_filters.append("v.capacity <= 50")
            elif capacity == 'medium':
                vendor_filters.append("v.capacity BETWEEN 51 AND 200")
            elif capacity == 'large':
                vendor_filters.append("v.capacity > 200")
        if location_id:
            vendor_filters.append("v.location_id = %s")
        if search_term:
            vendor_filters.append("v.name LIKE %s")

        if vendor_filters:
            vendor_query += " AND " + " AND ".join(vendor_filters)

        # Add filters to admin query
        admin_filters = []
        if capacity:
            if capacity == 'small':
                admin_filters.append("a.capacity <= 50")
            elif capacity == 'medium':
                admin_filters.append("a.capacity BETWEEN 51 AND 200")
            elif capacity == 'large':
                admin_filters.append("a.capacity > 200")
        if location_id:
            admin_filters.append("a.location_id = %s")
        if search_term:
            admin_filters.append("a.name LIKE %s")

        if admin_filters:
            admin_query += " AND " + " AND ".join(admin_filters)

        # Combine queries with UNION
        final_query = f"{vendor_query} UNION {admin_query}"

        # Prepare parameters for placeholders
        params = []
        if location_id:
            params.append(location_id)
        if search_term:
            params.append(f"%{search_term}%")
        if location_id:
            params.append(location_id)
        if search_term:
            params.append(f"%{search_term}%")

        cursor.execute(final_query, params)
        venues = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({'venues': venues})
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({'error': 'Failed to fetch venues'}), 500
    

@app.route('/get_services', methods=['GET'])
def get_services():
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch services from both vendor_services and admin_services tables
        cursor.execute("""
            SELECT name, price, 'vendor' AS source
            FROM vendor_services
            UNION
            SELECT name, price, 'admin' AS source
            FROM admin_services
        """)
        services = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({'services': services})
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({'error': 'Failed to fetch services'}), 500

    
@app.route('/submit_booking', methods=['POST'])
def submit_booking():
    if not session.get('user_signed_in'):
        return jsonify({'success': False, 'error': 'You must sign in to book a venue.'}), 403

    try:
        data = request.json
        booking_date = data['booking_date']
        venue_name = data['venue_name']
        location = data['location']
        event = data['event']
        services = data['services']  # List of selected service IDs

        # Convert numeric fields to float
        service_amount = float(data['service_amount'])
        venue_amount = float(data['venue_amount'])
        total_cost = float(data['total_cost'])
        payment_method = data['payment_method']

        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        # Verify that the user exists
        user_id = session.get('user_id')
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            cursor.close()
            connection.close()
            return jsonify({'success': False, 'error': 'User not found'}), 400

        # Fetch the venue ID, source, and vendor_id based on the venue name
        cursor.execute("""
            SELECT v.id, v.vendor_id, 'vendor' AS source FROM vendor_venues v WHERE v.name = %s
            UNION
            SELECT a.id, NULL AS vendor_id, 'admin' AS source FROM admin_venues a WHERE a.name = %s
        """, (venue_name, venue_name))
        venue = cursor.fetchone()

        if not venue:
            cursor.close()
            connection.close()
            return jsonify({'success': False, 'error': 'Venue not found'}), 400

        venue_id = venue['id']
        venue_source = venue['source']
        vendor_id = venue['vendor_id']  # Vendor ID is only applicable for vendor venues

        # Convert selected services into a comma-separated string
        services_string = ','.join(services)

        # Calculate distribution for venue cost
        venue_distribution = {}
        if venue_source == 'vendor':
            venue_distribution['vendor'] = venue_amount * 0.65
            venue_distribution['admin'] = venue_amount * 0.35
        elif venue_source == 'admin':
            venue_distribution['admin'] = venue_amount

        # Update wallet balance for venue owner
        if venue_source == 'vendor':
            cursor.execute("""
                UPDATE users
                SET wallet_balance = wallet_balance + %s
                WHERE id = %s
            """, (venue_distribution['vendor'], vendor_id))
        elif venue_source == 'admin':
            cursor.execute("""
                UPDATE admin_wallet
                SET balance = balance + %s
                WHERE id = 1
            """, (venue_distribution['admin'],))

        # Calculate distribution for service cost
        service_distribution = {'vendor': 0, 'admin': 0}
        if services:
            for service_id in services:
                cursor.execute("""
                    SELECT s.id, s.vendor_id, 'vendor' AS source FROM vendor_services s WHERE s.id = %s
                    UNION
                    SELECT s.id, NULL AS vendor_id, 'admin' AS source FROM admin_services s WHERE s.id = %s
                """, (service_id, service_id))
                service = cursor.fetchone()

                if service:
                    service_cost = service_amount / len(services)  # Divide service cost equally among services
                    if service['source'] == 'vendor':
                        service_distribution['vendor'] += service_cost * 0.65
                        service_distribution['admin'] += service_cost * 0.35

                        # Update vendor wallet balance
                        cursor.execute("""
                            UPDATE users
                            SET wallet_balance = wallet_balance + %s
                            WHERE id = %s
                        """, (service_cost * 0.65, service['vendor_id']))

                        # Update admin wallet balance for the remaining 35%
                        cursor.execute("""
                            UPDATE admin_wallet
                            SET balance = balance + %s
                            WHERE id = 1
                        """, (service_cost * 0.35,))
                    elif service['source'] == 'admin':
                        service_distribution['admin'] += service_cost

                        # Update admin wallet balance
                        cursor.execute("""
                            UPDATE admin_wallet
                            SET balance = balance + %s
                            WHERE id = 1
                        """, (service_cost,))

        # Insert booking into the appropriate table
        if venue_source == 'vendor':
            cursor.execute("""
                INSERT INTO vendor_bookings (user_id, vendor_id, venue_id, service_id, booking_date, event, service_amount, venue_amount, total_cost, payment_method, location)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, vendor_id, venue_id, services_string, booking_date, event, service_amount, venue_amount, total_cost, payment_method, location))
        elif venue_source == 'admin':
            cursor.execute("""
                INSERT INTO admin_bookings (user_id, venue_id, service_id, booking_date, event, service_amount, venue_amount, total_cost, payment_method, location)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, venue_id, services_string, booking_date, event, service_amount, venue_amount, total_cost, payment_method, location))

        # Update venue status to 'booked'
        if venue_source == 'vendor':
            cursor.execute("""
                UPDATE vendor_venues SET status = 'booked' WHERE id = %s
            """, (venue_id,))
        elif venue_source == 'admin':
            cursor.execute("""
                UPDATE admin_venues SET status = 'booked' WHERE id = %s
            """, (venue_id,))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'venue_distribution': venue_distribution,
            'service_distribution': service_distribution
        })
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({'success': False, 'error': str(err)}), 500
        

def update_venue_status():
    """Update venue status to 'available' if no bookings exist for the venue."""
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        # Update vendor venues
        cursor.execute("""
            UPDATE vendor_venues
            SET status = 'available'
            WHERE id NOT IN (SELECT venue_id FROM vendor_bookings) AND status = 'booked'
        """)

        # Update admin venues
        cursor.execute("""
            UPDATE admin_venues
            SET status = 'available'
            WHERE id NOT IN (SELECT venue_id FROM admin_bookings) AND status = 'booked'
        """)

        connection.commit()
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error updating venue status: {err}")

@app.route('/delete_booking', methods=['POST'])
def delete_booking():
    try:
        data = request.json
        booking_id = data['booking_id']  # ID of the booking to be deleted

        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch the venue ID and source associated with the booking
        cursor.execute("""
            SELECT venue_id, 'vendor' AS source FROM vendor_bookings WHERE id = %s
            UNION
            SELECT venue_id, 'admin' AS source FROM admin_bookings WHERE id = %s
        """, (booking_id, booking_id))
        booking = cursor.fetchone()

        if not booking:
            cursor.close()
            connection.close()
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        venue_id = booking['venue_id']
        venue_source = booking['source']

        # Delete the booking from the appropriate table
        if venue_source == 'vendor':
            cursor.execute("DELETE FROM vendor_bookings WHERE id = %s", (booking_id,))
        elif venue_source == 'admin':
            cursor.execute("DELETE FROM admin_bookings WHERE id = %s", (booking_id,))

        # Update venue status to 'available'
        if venue_source == 'vendor':
            cursor.execute("""
                UPDATE vendor_venues SET status = 'available' WHERE id = %s
            """, (venue_id,))
        elif venue_source == 'admin':
            cursor.execute("""
                UPDATE admin_venues SET status = 'available' WHERE id = %s
            """, (venue_id,))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'success': True, 'message': 'Booking deleted and venue status updated'})
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({'success': False, 'error': str(err)}), 500

@app.route('/venue/<venue_id>', methods=['GET'])
def venue_details(venue_id):
    try:
        print(f"Fetching details for venue ID: {venue_id}")
        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        # Try vendor_venues first
        cursor.execute("""
            SELECT v.name, v.description, v.capacity, v.price, v.image_path, l.address AS location
            FROM vendor_venues v
            LEFT JOIN vendor_locations l ON v.location_id = l.id
            WHERE v.id = %s
        """, (venue_id,))
        venue = cursor.fetchone()

        # If not found in vendor_venues, try admin_venues
        if not venue:
            cursor.execute("""
                SELECT a.name, a.description, a.capacity, a.price, a.image_path, al.address AS location
                FROM admin_venues a
                LEFT JOIN admin_locations al ON a.location_id = al.id
                WHERE a.id = %s
            """, (venue_id,))
            venue = cursor.fetchone()

        cursor.close()
        connection.close()

        if not venue:
            return jsonify({'error': 'Venue not found'}), 404

        return render_template('venueDetails.html', venue=venue)
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({'error': 'Failed to fetch venue details'}), 500



if __name__ == '__main__':
    app.run(debug=True)
