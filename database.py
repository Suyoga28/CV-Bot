import sqlite3
import aiosqlite
import asyncio


async def init_db():
    """Initialize the SQLite database asynchronously."""
    async with aiosqlite.connect("users.db") as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT,
                email TEXT
            )
        ''')
        
        try:
            await conn.execute("ALTER TABLE users ADD COLUMN name TEXT;")
        except aiosqlite.OperationalError:
            pass  # Column already exists, ignore error
        
        # Check if 'email' column exists, if not, add it
        try:
            await conn.execute("ALTER TABLE users ADD COLUMN email TEXT;")
        except aiosqlite.OperationalError:
            pass  # Column already exists, ignore error
        
        await conn.commit()

async def register_user(user_id, username, password, name, email):
    """Register a new user in the database."""
    try:
        async with aiosqlite.connect("users.db") as conn:
            await conn.execute(
                "INSERT INTO users ( username, password, name, email) VALUES (?, ?, ?)",
                (user_id, username, password, name, email),
            )
            await conn.commit()
        return True  # Registration successful
    except aiosqlite.IntegrityError:
        return False  # User already exists

async def authenticate_user(username, password):
    """Authenticate user asynchronously."""
    async with aiosqlite.connect("users.db") as conn:
        async with conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
        ) as cursor:
            user = await cursor.fetchone()
    return user is not None  # Returns True if user exists, False otherwise

async def is_user_registered(user_id):
    """Check if a user is already registered."""
    async with aiosqlite.connect("users.db") as conn:
        async with conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
    return user is not None  # Returns True if user exists, False otherwise

# Initialize the database (run only once)
if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
    print("Database initialized.")
