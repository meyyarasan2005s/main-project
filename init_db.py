import sqlite3
import os

# Delete any existing database
if os.path.exists('cropcare.db'):
    os.remove('cropcare.db')
    print("✅ Deleted old database")

# Create new database
conn = sqlite3.connect('cropcare.db')
cursor = conn.cursor()

# Create user table with mobile column
cursor.execute('''
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    mobile VARCHAR(20) NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    user_type VARCHAR(20) DEFAULT 'farmer',
    location VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Create crop_listing table
cursor.execute('''
CREATE TABLE crop_listing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop_name VARCHAR(100) NOT NULL,
    quantity FLOAT NOT NULL,
    unit VARCHAR(20) DEFAULT 'kg',
    price_per_unit FLOAT NOT NULL,
    location VARCHAR(200),
    description TEXT,
    image_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'available',
    seller_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(seller_id) REFERENCES user(id)
)
''')

# Create alert table
cursor.execute('''
CREATE TABLE alert (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    alert_type VARCHAR(50) DEFAULT 'info',
    user_id INTEGER NOT NULL,
    read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES user(id)
)
''')

# Create disease_history table
cursor.execute('''
CREATE TABLE disease_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    image_path VARCHAR(500),
    disease_name VARCHAR(200),
    confidence FLOAT,
    crop_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES user(id)
)
''')

conn.commit()
conn.close()

print("\n✅ Database created successfully!")
print("Tables created:")
print("  - user (with mobile column)")
print("  - crop_listing")
print("  - alert")
print("  - disease_history")