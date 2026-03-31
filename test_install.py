import sys
print(f"Python: {sys.version}")

try:
    import flask
    print(f"✅ Flask: {flask.__version__}")
except: print("❌ Flask missing")

try:
    import flask_sqlalchemy
    print(f"✅ Flask-SQLAlchemy: {flask_sqlalchemy.__version__}")
except: print("❌ Flask-SQLAlchemy missing")

try:
    import flask_login
    print(f"✅ Flask-Login: {flask_login.__version__}")
except: print("❌ Flask-Login missing")

try:
    from PIL import Image
    print(f"✅ Pillow: {Image.__version__}")
except: print("❌ Pillow missing")

try:
    import numpy
    print(f"✅ NumPy: {numpy.__version__}")
except: print("❌ NumPy missing")

try:
    import tensorflow as tf
    print(f"✅ TensorFlow: {tf.__version__}")
except: print("❌ TensorFlow missing")

try:
    import dotenv
    print(f"✅ python-dotenv: {dotenv.__version__}")
except: print("❌ python-dotenv missing")

print("\n" + "="*50)
print("Setup verification complete!")