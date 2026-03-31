# Agricultural Disease Detection & Crop Marketplace

A comprehensive web application for crop disease detection using deep learning and a marketplace platform for buying and selling agricultural products.

## Features

- **🌾 Crop Disease Detection**: AI-powered disease detection using a pre-trained VGG16 neural network
- **📊 Crop Recommendation**: Get personalized crop recommendations based on your region
- **🛒 Marketplace**: Buy and sell crops in an integrated marketplace
- **👤 User Authentication**: Secure login and registration system
- **📱 Responsive Design**: Works seamlessly across all devices
- **🗺️ Crop Guide**: Comprehensive guide for various crops

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite with SQLAlchemy ORM
- **Machine Learning**: TensorFlow/Keras (VGG16 model)
- **Model Format**: .keras files for disease classification

## Project Structure

```
├── app.py                          # Main Flask application
├── app_simple.py                   # Simplified version
├── requirements.txt                # Python dependencies
├── best_vgg16_scratch.keras        # Pre-trained VGG16 model (ML model)
├── class_indices_vgg16_scratch.json # Disease class mappings
├── crop_recommendation.json        # Crop recommendation data
├── remedy_database.json            # Disease remedies database
│
├── instance/                       # Instance-specific files
├── templates/                      # HTML templates
│   ├── base.html                   # Base template
│   ├── index.html                  # Home page
│   ├── login.html                  # Login page
│   ├── register.html               # Registration page
│   ├── dashboard.html              # User dashboard
│   ├── disease_detection.html      # Disease detection interface
│   ├── detection_result.html       # Detection results
│   ├── crop_guide.html             # Crop guide
│   ├── marketplace.html            # Marketplace
│   ├── add_listing.html            # Add marketplace listing
│   └── alerts.html                 # Alerts section
│
└── static/                         # Static files
    ├── css/
    │   └── style.css               # Styling
    ├── js/
    │   └── script.js               # Frontend scripts
    └── uploads/                    # User uploaded images
```

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/meyyarasan2005s/main-project.git
cd main-project
```

2. **Create a virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize the database**
```bash
python init_db.py
```

5. **Run the application**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### User Registration & Login
- Create an account via the registration page
- Login with your credentials
- Access your personalized dashboard

### Crop Disease Detection
1. Navigate to the Disease Detection section
2. Upload an image of a crop leaf or plant
3. The AI model will analyze the image and provide:
   - Disease diagnosis
   - Confidence score
   - Recommended remedies

### Crop Recommendations
- Visit the Crop Recommendation section
- Get AI-powered suggestions based on your region
- View detailed crop guides

### Marketplace
- Browse available crops from farmers
- List your own crops for sale
- Connect with buyers and sellers

## API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - User login
- `GET /logout` - User logout

### Disease Detection
- `POST /detect` - Upload and detect disease

### Marketplace
- `GET /marketplace` - View all listings
- `POST /add_listing` - Create new listing
- `GET /alerts` - View notifications

### Crop Information
- `GET /crop_guide` - View crop guide
- `GET /recommendation` - Get crop recommendations

## Database

The application uses SQLite with SQLAlchemy ORM. Key models include:
- **User**: User accounts and authentication
- **Listing**: Marketplace listings
- **Disease**: Disease information and remedies

Database initialization scripts:
- `init_db.py` - Initialize database
- `setup_db.py` - Setup database with initial data
- `fix_database.py` - Database repair utilities

## Machine Learning Model

### VGG16 Model
- **Architecture**: VGG16 (16-layer convolutional neural network)
- **Training**: Trained from scratch on crop disease dataset
- **Format**: Keras model (.keras)
- **Classes**: Multiple crop diseases loaded from `class_indices_vgg16_scratch.json`

### Disease Database
- Remedies and treatment information stored in `remedy_database.json`
- Comprehensive disease details for reference

## Configuration

### Environment Variables
Create a `.env` file in the root directory:
```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///instance/app.db
```

## Troubleshooting

### Database Issues
```bash
python fix_db.py  # Fix database corruption
python clean_db.py  # Clean database
```

### Version Checks
```bash
python check_versions.py  # Check package versions
```

### Installation Test
```bash
python test_install.py  # Test installation
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and suggestions.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Meyyarasan**

- GitHub: [@meyyarasan2005s](https://github.com/meyyarasan2005s)

## Acknowledgments

- TensorFlow/Keras for the deep learning framework
- Flask for the web framework
- Agricultural disease dataset providers
- Community contributors and testers

## Support

For support, email your-email@example.com or open an issue in the repository.

---

**Note**: The ML model file (`best_vgg16_scratch.keras`) is large and stored separately. Pull the latest version after cloning to ensure you have the trained model.
