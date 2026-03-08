import asyncio
from database import db
import bcrypt

def get_password_hash(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

async def add_users():
    users = [
        {"username": "delta", "password": "password4", "role": "participant"},
        {"username": "echo", "password": "password5", "role": "participant"},
        {"username": "foxtrot", "password": "password6", "role": "participant"},
        {"username": "golf", "password": "password7", "role": "participant"},
        {"username": "hotel", "password": "password8", "role": "participant"}
    ]
    
    for user_data in users:
        username = user_data["username"]
        password = user_data["password"]
        role = user_data["role"]
        
        existing_user = await db.users.find_one({"username": username})
        if existing_user:
            print(f"User {username} already exists. Updating password...")
            await db.users.update_one(
                {"username": username},
                {"$set": {
                    "hashed_password": get_password_hash(password),
                    "role": role
                }}
            )
            print("Updated successfully.")
        else:
            print(f"Creating new user {username}...")
            user_dict = {
                "username": username,
                "hashed_password": get_password_hash(password),
                "role": role
            }
            await db.users.insert_one(user_dict)
            print("Created successfully.")

if __name__ == "__main__":
    asyncio.run(add_users())
