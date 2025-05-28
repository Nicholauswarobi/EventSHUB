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
            password VARCHAR(200) NOT NULL
        )
        """)

        # Create locations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            address VARCHAR(255) NOT NULL,
            city VARCHAR(100) NOT NULL,
            state VARCHAR(100),
            country VARCHAR(100) NOT NULL
        )
        """)

        # Create venues table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS venues (
            id INT AUTO_INCREMENT PRIMARY KEY,
            location_id INT NOT NULL,
            name VARCHAR(120) NOT NULL UNIQUE,
            description TEXT,
            capacity INT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (location_id) REFERENCES locations(id)
        )
        """)

        # Create services table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(120) NOT NULL UNIQUE,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL
        )
        """)

        # Create events table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(120) NOT NULL UNIQUE,
            description TEXT,
            date DATE NOT NULL,
            venue_id INT NOT NULL,
            service_id INT NOT NULL,
            FOREIGN KEY (venue_id) REFERENCES venues(id),
            FOREIGN KEY (service_id) REFERENCES services(id)
        )
        """)

        # Create bookings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            event_id INT NOT NULL,
            date DATE NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
        """)

        # Create payments table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            booking_id INT NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            payment_date DATE NOT NULL,
            status VARCHAR(50) NOT NULL,
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
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

        # Hash the password
        hashed_password = generate_password_hash(password)

        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        # Insert user into the database
        cursor.execute("""
        INSERT INTO users (username, email, password)
        VALUES (%s, %s, %s)
        """, (username, email, hashed_password))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "User registered successfully!"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data['username']
        password = data['password']

        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch user from the database
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user and check_password_hash(user['password'], password):
            session['user_signed_in'] = True  # Set session to indicate user is signed in
            return jsonify({"message": "Login successful!"}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    except mysql.connector.Error as err:
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
    connection = connection_pool.get_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        try:
            print("Form data received:", request.form)  # Log the form data

            # Handle Add Location Form
            if 'submit_location' in request.form:
                address = request.form.get('address')
                city = request.form.get('city')
                state = request.form.get('state')
                country = request.form.get('country')
                print(f"Adding location: {address}, {city}, {state}, {country}")  # Debug log
                if address and city and country:
                    cursor.execute("""
                        INSERT INTO locations (address, city, state, country)
                        VALUES (%s, %s, %s, %s)
                    """, (address, city, state, country))
                    connection.commit()

            # Handle Add Venue Form
            elif 'submit_venue' in request.form:
                venue_name = request.form.get('venue_name')
                venue_description = request.form.get('venue_description')
                venue_capacity = request.form.get('venue_capacity')
                venue_price = request.form.get('venue_price')
                location_id = request.form.get('location_id')
                print(f"Adding venue: {venue_name}, {venue_description}, {venue_capacity}, {venue_price}, {location_id}")  # Debug log
                if venue_name and venue_capacity and venue_price and location_id:
                    cursor.execute("""
                        INSERT INTO venues (name, description, capacity, price, location_id)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (venue_name, venue_description, venue_capacity, venue_price, location_id))
                    connection.commit()

            # Handle Add Service Form
            elif 'submit_service' in request.form:
                service_name = request.form.get('service_name')
                service_description = request.form.get('service_description')
                service_price = request.form.get('service_price')
                print(f"Adding service: {service_name}, {service_description}, {service_price}")  # Debug log
                if service_name and service_price:
                    cursor.execute("""
                        INSERT INTO services (name, description, price)
                        VALUES (%s, %s, %s)
                    """, (service_name, service_description, service_price))
                    connection.commit()

            # Handle Add Event Form
            elif 'submit_event' in request.form:
                event_name = request.form.get('event_name')
                event_description = request.form.get('event_description')
                event_date = request.form.get('event_date')
                event_venue_id = request.form.get('event_venue_id')
                event_service_id = request.form.get('event_service_id')
                print(f"Adding event: {event_name}, {event_description}, {event_date}, {event_venue_id}, {event_service_id}")  # Debug log
                if event_name and event_date and event_venue_id:
                    cursor.execute("""
                        INSERT INTO events (name, description, date, venue_id, service_id)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (event_name, event_description, event_date, event_venue_id, event_service_id))
                    connection.commit()

        except Exception as e:
            print(f"Error: {e}")  # Log the error to the console
            return "An error occurred while processing your request. Please try again later.", 500
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('admin_dashboard'))

    # Fetch metrics and dropdown data
    cursor.execute("SELECT COUNT(*) AS total_users FROM users")
    total_users = cursor.fetchone()['total_users']

    cursor.execute("SELECT COUNT(*) AS available_venues FROM venues")
    available_venues = cursor.fetchone()['available_venues']

    cursor.execute("SELECT COUNT(*) AS total_vendors FROM users WHERE is_vendor = 1")
    total_vendors = cursor.fetchone()['total_vendors']

    cursor.execute("SELECT COUNT(*) AS total_services FROM services")
    total_services = cursor.fetchone()['total_services']

    cursor.execute("SELECT COUNT(*) AS booked_venues FROM bookings")
    booked_venues = cursor.fetchone()['booked_venues']

    cursor.execute("SELECT * FROM locations")
    locations = cursor.fetchall()

    cursor.execute("SELECT * FROM venues")
    venues = cursor.fetchall()

    cursor.execute("SELECT * FROM services")
    services = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        available_venues=available_venues,
        total_vendors=total_vendors,
        total_services=total_services,
        booked_venues=booked_venues,
        locations=locations,
        venues=venues,
        services=services
    )

if __name__ == '__main__':
    app.run(debug=True)
