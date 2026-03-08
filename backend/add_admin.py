import asyncio
from database import db
import bcrypt

def get_password_hash(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    # passlib stores hashes as string, so decode the bcrypt result
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

async def add_admin():
    username = "joopadmin"
    password = "Password1"
    
    # Check if user already exists
    existing_user = await db.users.find_one({"username": username})
    if existing_user:
        print(f"User {username} already exists. Updating password and role to admin...")
        await db.users.update_one(
            {"username": username},
            {"$set": {
                "hashed_password": get_password_hash(password),
                "role": "admin"
            }}
        )
        print("Updated successfully.")
    else:
        print(f"Creating new admin user {username}...")
        user_dict = {
            "username": username,
            "hashed_password": get_password_hash(password),
            "role": "admin"
        }
        await db.users.insert_one(user_dict)
        print("Created successfully.")

if __name__ == "__main__":
    asyncio.run(add_admin())
