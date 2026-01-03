from app import create_app
from backend.models import db, User
from backend.extensions import bcrypt

app = create_app()

def create_admin_user(username, email, password):
    with app.app_context():
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"User with email {email} already exists. Updating role to admin.")
            existing_user.role = 'admin'
            db.session.commit()
            return

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_admin = User(username=username, email=email, password=hashed_password, role='admin')
        db.session.add(new_admin)
        db.session.commit()
        print(f"Admin user {username} ({email}) created successfully.")

if __name__ == "__main__":
    print("Creating Admin User...")
    u = input("Username: ")
    e = input("Email: ")
    p = input("Password: ")
    create_admin_user(u, e, p)
