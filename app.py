import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cropcare-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cropcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create upload folder if not exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==================== DATABASE MODELS ====================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
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
    image_url = db.Column(db.String(500))
    status = db.Column(db.String(20), default='available')
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    seller = db.relationship('User', backref='listings')

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    alert_type = db.Column(db.String(50), default='info')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='alerts')

class DiseaseHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(500))
    disease_name = db.Column(db.String(200))
    confidence = db.Column(db.Float)
    crop_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='disease_history')

# Create database - SIMPLE creation, NO column addition
with app.app_context():
    db.create_all()
    print("✅ Database ready")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== MOCK DISEASE DETECTION ====================
class MockDiseaseDetector:
    def predict(self, image_bytes):
        import random
        diseases = [
            "Tomato___Early_blight", 
            "Tomato___Late_blight", 
            "Tomato___healthy",
            "Potato___Early_blight",
            "Potato___Late_blight",
            "Potato___healthy"
        ]
        disease = random.choice(diseases)
        confidence = random.uniform(0.75, 0.95)
        
        if "Early_blight" in disease:
            name = "Early Blight"
            symptoms = ["Dark brown spots with concentric rings", "Yellowing of lower leaves", "Target-like lesions"]
            organic = ["Copper fungicides", "Baking soda spray (1 tbsp per gallon)", "Neem oil spray"]
            chemical = ["Chlorothalonil: 2ml per liter", "Mancozeb: 2g per liter"]
            prevention = ["Crop rotation", "Mulch to prevent soil splash", "Water at base", "Remove infected leaves"]
        elif "Late_blight" in disease:
            name = "Late Blight"
            symptoms = ["Water-soaked spots on leaves", "White fuzzy mold on undersides", "Rapid spread"]
            organic = ["Copper fungicides", "Remove infected plants", "Improve air circulation"]
            chemical = ["Metalaxyl", "Mancozeb", "Chlorothalonil"]
            prevention = ["Use certified seed", "Crop rotation", "Avoid overhead irrigation"]
        else:
            name = "Healthy Plant"
            symptoms = ["No disease symptoms", "Healthy green leaves", "Normal growth"]
            organic = ["Continue organic practices", "Apply compost tea monthly"]
            chemical = ["No treatment needed"]
            prevention = ["Regular monitoring", "Proper nutrition", "Good field hygiene"]
        
        remedy_info = {
            "name": name,
            "symptoms": symptoms,
            "organic_treatments": organic,
            "chemical_treatments": chemical,
            "prevention": prevention
        }
        
        return {
            'disease_class': disease,
            'disease_name': name,
            'confidence': confidence,
            'remedy_info': remedy_info
        }

detector = MockDiseaseDetector()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

# ==================== ROUTES ====================
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        user_type = request.form.get('user_type', 'farmer')
        location = request.form.get('location', '')
        
        # Validate mobile number (10 digits)
        if not mobile or not mobile.isdigit() or len(mobile) != 10:
            flash('Please enter a valid 10-digit mobile number', 'error')
            return redirect(url_for('register'))
        
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
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    listings_count = CropListing.query.filter_by(seller_id=current_user.id).count()
    detections_count = DiseaseHistory.query.filter_by(user_id=current_user.id).count()
    unread_alerts = Alert.query.filter_by(user_id=current_user.id, read=False).count()
    
    total_listings = CropListing.query.filter_by(status='available').count()
    marketplace_listings = CropListing.query.filter_by(status='available').order_by(CropListing.created_at.desc()).limit(5).all()
    
    for listing in marketplace_listings:
        seller = User.query.get(listing.seller_id)
        listing.seller_name = seller.username if seller else 'Unknown'
        listing.seller_mobile = seller.mobile if seller else 'Not provided'
        listing.seller_email = seller.email if seller else 'Not provided'
    
    recent_detections = DiseaseHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(DiseaseHistory.created_at.desc()).limit(5).all()
    
    recent_listings = CropListing.query.filter_by(
        seller_id=current_user.id
    ).order_by(CropListing.created_at.desc()).limit(5).all()
    
    recent_alerts = Alert.query.filter_by(
        user_id=current_user.id
    ).order_by(Alert.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         listings_count=listings_count,
                         detections_count=detections_count,
                         unread_alerts=unread_alerts,
                         total_listings=total_listings,
                         marketplace_listings=marketplace_listings,
                         recent_detections=recent_detections,
                         recent_listings=recent_listings,
                         recent_alerts=recent_alerts)

@app.route('/disease-detection', methods=['GET', 'POST'])
@login_required
def disease_detection():
    if current_user.user_type != 'farmer':
        flash('This feature is only available for farmers.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload JPG, PNG, or JPEG', 'error')
            return redirect(request.url)
        
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        crop_type = request.form.get('crop_type', 'Unknown')
        location = request.form.get('location', current_user.location or '')
        
        with open(filepath, 'rb') as f:
            image_bytes = f.read()
        
        result = detector.predict(image_bytes)
        detection_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        detection = DiseaseHistory(
            user_id=current_user.id,
            image_path=unique_filename,
            disease_name=result['disease_class'],
            confidence=result['confidence'],
            crop_type=crop_type
        )
        db.session.add(detection)
        
        if 'healthy' not in result['disease_class'].lower():
            alert = Alert(
                title=f"Disease Detected: {result['disease_name']}",
                message=f"Your {crop_type} crop shows {result['disease_name']}.",
                alert_type='disease',
                user_id=current_user.id
            )
            db.session.add(alert)
        
        db.session.commit()
        
        return render_template('detection_result.html',
                             image_url=url_for('static', filename=f'uploads/{unique_filename}'),
                             result=result,
                             crop_type=crop_type,
                             location=location,
                             detection_time=detection_time)
    
    return render_template('disease_detection.html')

@app.route('/marketplace')
@login_required
def marketplace():
    crop_name = request.args.get('crop_name', '')
    location = request.args.get('location', '')
    
    query = CropListing.query.filter_by(status='available')
    
    if crop_name:
        query = query.filter(CropListing.crop_name.ilike(f'%{crop_name}%'))
    if location:
        query = query.filter(CropListing.location.ilike(f'%{location}%'))
    
    listings = query.order_by(CropListing.created_at.desc()).all()
    
    for listing in listings:
        seller = User.query.get(listing.seller_id)
        listing.seller_name = seller.username if seller else 'Unknown'
        listing.seller_mobile = seller.mobile if seller else 'Not provided'
        listing.seller_email = seller.email if seller else 'Not provided'
    
    return render_template('marketplace.html', listings=listings)

@app.route('/add-listing', methods=['GET', 'POST'])
@login_required
def add_listing():
    if current_user.user_type != 'farmer':
        flash('Only farmers can add listings.', 'error')
        return redirect(url_for('marketplace'))
    
    if request.method == 'POST':
        try:
            crop_name = request.form.get('crop_name')
            quantity = float(request.form.get('quantity', 0))
            unit = request.form.get('unit', 'kg')
            price = float(request.form.get('price_per_unit', 0))
            location = request.form.get('location', current_user.location or '')
            description = request.form.get('description', '')
            
            image_url = ''
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    if allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        unique_filename = f"{uuid.uuid4().hex}_{filename}"
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                        file.save(filepath)
                        image_url = unique_filename
            
            listing = CropListing(
                crop_name=crop_name,
                quantity=quantity,
                unit=unit,
                price_per_unit=price,
                location=location,
                description=description,
                image_url=image_url,
                seller_id=current_user.id
            )
            
            db.session.add(listing)
            db.session.commit()
            
            flash('Crop listing added successfully!', 'success')
            return redirect(url_for('marketplace'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('add_listing.html')

@app.route('/crop-guide')
@login_required
def crop_guide():
    if current_user.user_type != 'farmer':
        flash('This feature is only available for farmers.', 'error')
        return redirect(url_for('dashboard'))
    
    season = request.args.get('season', 'winter')
    soil_type = request.args.get('soil_type', 'loamy')
    
    crop_recommendations = {
        "season_based": {
            "winter": [
                {"crop": "Wheat", "months": ["Nov", "Dec", "Jan"], "temp_range": "10-25°C"},
                {"crop": "Barley", "months": ["Nov", "Dec"], "temp_range": "10-20°C"},
                {"crop": "Mustard", "months": ["Oct", "Nov"], "temp_range": "15-30°C"}
            ],
            "summer": [
                {"crop": "Rice", "months": ["Jun", "Jul"], "temp_range": "25-35°C"},
                {"crop": "Maize", "months": ["Mar", "Apr"], "temp_range": "20-30°C"}
            ],
            "rainy": [
                {"crop": "Sugarcane", "months": ["Jul", "Aug"], "temp_range": "20-30°C"},
                {"crop": "Groundnut", "months": ["Jun", "Jul"], "temp_range": "25-35°C"}
            ]
        },
        "soil_based": {
            "sandy": [
                {"crop": "Watermelon", "ph_range": "6.0-7.0"},
                {"crop": "Carrot", "ph_range": "5.5-7.0"}
            ],
            "clay": [
                {"crop": "Rice", "ph_range": "5.5-6.5"},
                {"crop": "Cabbage", "ph_range": "6.0-7.0"}
            ],
            "loamy": [
                {"crop": "Tomato", "ph_range": "6.0-7.0"},
                {"crop": "Wheat", "ph_range": "6.0-7.5"}
            ]
        }
    }
    
    season_crops = crop_recommendations.get('season_based', {}).get(season, [])
    soil_crops = crop_recommendations.get('soil_based', {}).get(soil_type, [])
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    current_month = month_names[datetime.now().month - 1]
    
    best_crops = []
    for crop_item in season_crops:
        if current_month in crop_item.get('months', []):
            best_crops.append(crop_item)
    
    return render_template('crop_guide.html',
                         season=season,
                         soil_type=soil_type,
                         season_crops=season_crops,
                         soil_crops=soil_crops,
                         best_crops=best_crops,
                         current_month=current_month)

@app.route('/alerts')
@login_required
def alerts():
    if current_user.user_type != 'farmer':
        flash('This feature is only available for farmers.', 'error')
        return redirect(url_for('dashboard'))
    
    Alert.query.filter_by(user_id=current_user.id, read=False).update({'read': True})
    db.session.commit()
    
    user_alerts = Alert.query.filter_by(
        user_id=current_user.id
    ).order_by(Alert.created_at.desc()).all()
    
    return render_template('alerts.html', alerts=user_alerts)

@app.route('/update-listing/<int:listing_id>', methods=['POST'])
@login_required
def update_listing(listing_id):
    listing = CropListing.query.get_or_404(listing_id)
    
    if listing.seller_id != current_user.id:
        return jsonify({'success': False, 'error': 'You do not have permission to edit this listing'})
    
    try:
        listing.crop_name = request.form.get('crop_name')
        listing.quantity = float(request.form.get('quantity'))
        listing.unit = request.form.get('unit')
        listing.price_per_unit = float(request.form.get('price_per_unit'))
        listing.location = request.form.get('location')
        listing.description = request.form.get('description')
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Listing updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/delete-listing/<int:listing_id>', methods=['POST'])
@login_required
def delete_listing(listing_id):
    listing = CropListing.query.get_or_404(listing_id)
    
    if listing.seller_id != current_user.id:
        return jsonify({'success': False, 'error': 'You do not have permission to delete this listing'})
    
    try:
        db.session.delete(listing)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/mark-sold/<int:listing_id>', methods=['POST'])
@login_required
def mark_sold(listing_id):
    listing = CropListing.query.get_or_404(listing_id)
    
    if listing.seller_id != current_user.id:
        return jsonify({'success': False, 'error': 'You do not have permission to modify this listing'})
    
    try:
        listing.status = 'sold'
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting CropCare Assistant Server")
    print("="*60)
    print("🌐 Access at: http://localhost:5000")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)