import sqlite3
import bcrypt
from cryptography.fernet import Fernet


def create_connection():
    conn = sqlite3.connect('prescriptions.db')  
    return conn


def create_tables():
    conn = create_connection()
    c = conn.cursor()

    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL)''')

    
    c.execute('''CREATE TABLE IF NOT EXISTS prescriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    original_prescription TEXT,  -- To store original prescription text
                    encrypted_prescription TEXT,  -- To store encrypted prescription text
                    encrypted_image BLOB,         -- To store encrypted image data
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- To store the creation date
                    FOREIGN KEY(user_id) REFERENCES users(id))''')

    conn.commit()  
    conn.close()   


def hash_password(password):
    salt = bcrypt.gensalt()  
    hashed_password = bcrypt.hashpw(password.encode(), salt)  
    return hashed_password


def verify_password(stored_hash, entered_password):
    return bcrypt.checkpw(entered_password.encode(), stored_hash)  


def add_user(email, password):
    conn = create_connection()
    c = conn.cursor()

    
    hashed_password = hash_password(password)

    
    c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
    
    conn.commit()  # Save changes
    conn.close()   # Close the connection


def verify_user(email, password):
    conn = create_connection()
    c = conn.cursor()

    
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()  
    conn.close()

    if user:
        
        stored_hash = user[2]  
        if verify_password(stored_hash, password):
            return True  
        else:
            return False  
    else:
        return False  


def add_prescription(user_id, original_prescription, encrypted_prescription):
    conn = create_connection()
    c = conn.cursor()

    
    c.execute('''INSERT INTO prescriptions (user_id, original_prescription, encrypted_prescription)
                 VALUES (?, ?, ?)''', (user_id, original_prescription, encrypted_prescription))

    conn.commit()  # Save changes
    conn.close()   # Close the connection


def add_prescription_image(user_id, encrypted_image):
    conn = create_connection()
    c = conn.cursor()

    
    c.execute('''UPDATE prescriptions SET encrypted_image = ? WHERE user_id = ?''',
              (encrypted_image, user_id))

    conn.commit()  
    conn.close()   


def generate_key():
    return Fernet.generate_key()


def encrypt_prescription(prescription, key):
    f = Fernet(key)
    encrypted_prescription = f.encrypt(prescription.encode())  
    return encrypted_prescription


def encrypt_image(image_data, key):
    f = Fernet(key)
    encrypted_image = f.encrypt(image_data) 
    return encrypted_image


def decrypt_image(encrypted_image, key):
    """
    Decrypts the encrypted image using the provided encryption key.
    """
    f = Fernet(key)
    decrypted_image = f.decrypt(encrypted_image)  
    return decrypted_image


def get_prescriptions(user_id):
    conn = create_connection()
    c = conn.cursor()

    
    c.execute("SELECT original_prescription, encrypted_prescription, encrypted_image, created_at FROM prescriptions WHERE user_id = ?", (user_id,))
    prescriptions = c.fetchall()

    conn.close()

    return prescriptions


def add_encrypted_image_column():
    conn = create_connection()
    c = conn.cursor()

    # Check if the 'encrypted_image' column exists
    c.execute("PRAGMA table_info(prescriptions)")
    columns = [column[1] for column in c.fetchall()]

    # If the column doesn't exist, add it
    if "encrypted_image" not in columns:
        c.execute("ALTER TABLE prescriptions ADD COLUMN encrypted_image BLOB")
        print("Column 'encrypted_image' added to prescriptions table.")

    conn.commit()
    conn.close()


def setup_database():
    create_tables()  
    add_encrypted_image_column()  