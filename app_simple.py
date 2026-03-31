from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cropcare-secret-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cropcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(20))
    password_hash = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), default='farmer')
    location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class CropListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='kg')
    price_per_unit = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='available')
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    seller = db.relationship('User', backref='listings')

# Create database
with app.app_context():
    db.create_all()
    print("Database created successfully")

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>CropCare Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f0f0; }
        .container { max-width: 1200px; margin: auto; background: white; padding: 20px; border-radius: 10px; }
        .navbar { background: #2e7d32; color: white; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        .navbar a { color: white; text-decoration: none; margin-right: 20px; }
        .btn { display: inline-block; padding: 10px 20px; background: #4caf50; color: white; text-decoration: none; border-radius: 5px; }
        .card { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; background: white; }
        .alert { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .alert-success { background: #d4edda; color: #155724; }
        .alert-error { background: #f8d7da; color: #721c24; }
        input, select, textarea { width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #4caf50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .listing-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }
        .listing-card { border: 1px solid #ddd; padding: 15px; border-radius: 5px; background: white; }
        .price { font-size: 24px; color: #2e7d32; font-weight: bold; }
        .contact-info { background: #e8f5e9; padding: 10px; margin-top: 10px; border-radius: 5px; }
        .float-right { float: right; }
        h1, h2 { color: #2e7d32; }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="/">Home</a>
        {% if session.user_id %}
            <a href="/dashboard">Dashboard</a>
            <a href="/marketplace">Marketplace</a>
            {% if session.user_type == 'farmer' %}
                <a href="/add-listing">Sell Crop</a>
            {% endif %}
            <span class="float-right">Welcome, {{ session.username }} | <a href="/logout">Logout</a></span>
        {% else %}
            <span class="float-right"><a href="/login">Login</a> | <a href="/register">Register</a></span>
        {% endif %}
    </div>
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
</body>
</html>
'''

def login_required(f):
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE + '''
    {% block content %}
    <div style="text-align: center; padding: 50px;">
        <h1>CropCare Assistant</h1>
        <p style="font-size: 18px;">AI-powered crop disease detection and marketplace platform</p>
        {% if not session.user_id %}
        <p><a href="/register" class="btn">Get Started</a> <a href="/login" class="btn">Login</a></p>
        {% else %}
        <p><a href="/dashboard" class="btn">Go to Dashboard</a></p>
        {% endif %}
    </div>
    {% endblock %}
    ''')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        user_type = request.form.get('user_type', 'farmer')
        location = request.form.get('location', '')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email, mobile=mobile, user_type=user_type, location=location)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template_string(HTML_TEMPLATE + '''
    {% block content %}
    <h2>Register</h2>
    <form method="POST">
        <label>Username:</label>
        <input type="text" name="username" required>
        <label>Email:</label>
        <input type="email" name="email" required>
        <label>Mobile Number:</label>
        <input type="text" name="mobile" required>
        <label>Password:</label>
        <input type="password" name="password" required>
        <label>User Type:</label>
        <select name="user_type">
            <option value="farmer">Farmer</option>
            <option value="buyer">Buyer</option>
        </select>
        <label>Location:</label>
        <input type="text" name="location">
        <button type="submit">Register</button>
    </form>
    <p>Already have an account? <a href="/login">Login here</a></p>
    {% endblock %}
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_type'] = user.user_type
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template_string(HTML_TEMPLATE + '''
    {% block content %}
    <h2>Login</h2>
    <form method="POST">
        <label>Username:</label>
        <input type="text" name="username" required>
        <label>Password:</label>
        <input type="password" name="password" required>
        <button type="submit">Login</button>
    </form>
    <p>Don't have an account? <a href="/register">Register here</a></p>
    {% endblock %}
    ''')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    listings_count = CropListing.query.filter_by(seller_id=user.id).count()
    
    content = f'''
    <h1>Welcome, {user.username}!</h1>
    <div class="card">
        <h3>Profile Details</h3>
        <p><strong>Email:</strong> {user.email}</p>
        <p><strong>Mobile:</strong> {user.mobile or 'Not provided'}</p>
        <p><strong>Location:</strong> {user.location or 'Not specified'}</p>
        <p><strong>Account Type:</strong> {user.user_type.title()}</p>
        <p><strong>Active Listings:</strong> {listings_count}</p>
    </div>
    <p><a href="/marketplace" class="btn">Browse Marketplace</a>
    '''
    
    if session['user_type'] == 'farmer':
        content += '<a href="/add-listing" class="btn">Add New Listing</a>'
    
    content += '</p>'
    
    return render_template_string(HTML_TEMPLATE + '{% block content %}' + content + '{% endblock %}')

@app.route('/marketplace')
@login_required
def marketplace():
    listings = CropListing.query.filter_by(status='available').order_by(CropListing.created_at.desc()).all()
    
    if listings:
        listings_html = '<div class="listing-grid">'
        for listing in listings:
            seller = User.query.get(listing.seller_id)
            total_value = listing.quantity * listing.price_per_unit
            
            listings_html += f'''
            <div class="listing-card">
                <h3>{listing.crop_name}</h3>
                <div class="price">₹{listing.price_per_unit}/{listing.unit}</div>
                <p><strong>Quantity:</strong> {listing.quantity} {listing.unit}</p>
                <p><strong>Total Value:</strong> ₹{total_value:.2f}</p>
                <p><strong>Location:</strong> {listing.location or 'Not specified'}</p>
                <p><strong>Seller:</strong> {seller.username}</p>
            '''
            
            if session['user_type'] == 'buyer' and session['user_id'] != listing.seller_id:
                listings_html += f'''
                <div class="contact-info">
                    <strong>Contact Seller:</strong><br>
                    Phone: {seller.mobile or 'Not provided'}<br>
                    Email: {seller.email}<br>
                    Location: {seller.location or 'Not specified'}
                </div>
                '''
            elif session['user_id'] == listing.seller_id:
                listings_html += '<p><em>This is your listing</em></p>'
            
            listings_html += '</div>'
        listings_html += '</div>'
    else:
        listings_html = '<p>No listings available.</p>'
    
    return render_template_string(HTML_TEMPLATE + f'''
    {% block content %}
    <h1>Marketplace</h1>
    <p>Total Listings: {len(listings)}</p>
    {listings_html}
    <p><a href="/dashboard" class="btn">Back to Dashboard</a></p>
    {% endblock %}
    ''')

@app.route('/add-listing', methods=['GET', 'POST'])
@login_required
def add_listing():
    if session['user_type'] != 'farmer':
        flash('Only farmers can add listings', 'error')
        return redirect(url_for('marketplace'))
    
    if request.method == 'POST':
        crop_name = request.form.get('crop_name')
        quantity = float(request.form.get('quantity', 0))
        unit = request.form.get('unit', 'kg')
        price = float(request.form.get('price_per_unit', 0))
        location = request.form.get('location', '')
        description = request.form.get('description', '')
        
        listing = CropListing(
            crop_name=crop_name,
            quantity=quantity,
            unit=unit,
            price_per_unit=price,
            location=location,
            description=description,
            seller_id=session['user_id']
        )
        
        db.session.add(listing)
        db.session.commit()
        
        flash('Crop listing added successfully!', 'success')
        return redirect(url_for('marketplace'))
    
    return render_template_string(HTML_TEMPLATE + '''
    {% block content %}
    <h2>Add Crop Listing</h2>
    <form method="POST">
        <label>Crop Name:</label>
        <input type="text" name="crop_name" required>
        
        <label>Quantity:</label>
        <input type="number" name="quantity" step="0.1" required>
        
        <label>Unit:</label>
        <select name="unit">
            <option value="kg">kg</option>
            <option value="quintal">Quintal</option>
            <option value="ton">Ton</option>
        </select>
        
        <label>Price per Unit (₹):</label>
        <input type="number" name="price_per_unit" step="0.01" required>
        
        <label>Location:</label>
        <input type="text" name="location">
        
        <label>Description:</label>
        <textarea name="description" rows="3"></textarea>
        
        <button type="submit">Add Listing</button>
        <a href="/marketplace" class="btn">Cancel</a>
    </form>
    {% endblock %}
    ''')

if __name__ == '__main__':
    print("\n" + "="*50)
    print("CropCare Assistant Server Starting...")
    print("Open: http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)