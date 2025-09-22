# User authentication utilities using werkzeug.security
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password):
	"""
	Hash a plain-text password securely.
	"""
	return generate_password_hash(password)

def check_password(hashed_password, password):
	"""
	Compare a hashed password with a plain-text password.
	Returns True if they match, False otherwise.
	"""
	return check_password_hash(hashed_password, password)
