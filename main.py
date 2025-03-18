import requests
import os
import asyncio
import re
from pdf_generator import generate_pdf  # Ensure this module exists
import telegram.error
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext, ContextTypes

# Load environment variables
load_dotenv()

MONKEY_API_URL = "https://api.pdfmonkey.io/api/v1" 
MONKEY_API_KEY = os.getenv("MONKEY_API_KEY")
bot_token = os.getenv("BOT_TOKEN")

if not bot_token:
    raise ValueError("BOT_TOKEN is missing in the .env file")
if not MONKEY_API_KEY:
    raise ValueError("🚨 MONKEY_API_KEY is missing in the .env file!")

# Define conversation states
NAME, EMAIL, PHONE, OBJECTIVE, EDUCATION, SKILLS, EXPERIENCE, PROJECTS, VOLUNTEER, ACHIEVEMENTS, LEETCODE, GITHUB = range(12)

# Store user data
user_data = {} 

def call_monkey_api(data):
    headers = {
        "Authorization": f"Bearer {MONKEY_API_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.post(MONKEY_API_URL, json=data, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# Load environment variables
load_dotenv()
bot_token = os.getenv("BOT_TOKEN")

if not bot_token:
    raise ValueError("BOT_TOKEN is missing in the .env file")

# Define conversation states
NAME, EMAIL, PHONE, OBJECTIVE, EDUCATION, SKILLS, EXPERIENCE, PROJECTS, VOLUNTEER, ACHIEVEMENTS, LEETCODE, GITHUB = range(12)

# Store user data
user_data = {}

# Function to safely send messages with timeout handling
async def safe_send_message(update, text, retries=3):
    for attempt in range(retries):
        try:
            await update.message.reply_text(text)
            await asyncio.sleep(0.5)
            return
        except (telegram.error.TimedOut, telegram.error.NetworkError):
            if attempt < retries - 1:
                print(f"⚠️ Error sending message. Retrying {attempt + 1}/{retries}...")
                await asyncio.sleep(5)
            else:
                print("❌ Failed to send message after multiple attempts.")

# Function to safely send documents (like PDFs)
async def safe_send_document(update, file_path):
    try:
        with open(file_path, "rb") as file:
            await update.message.reply_document(document=file)
    except telegram.error.TimedOut:
        print("⚠️ File sending timed out! Retrying in 5 seconds⏳...")
        await asyncio.sleep(5)
        await safe_send_document(update, file_path)
    except telegram.error.NetworkError:
        print("⚠️ Network error! Retrying in 10 seconds⏳...")
        await asyncio.sleep(10)
        await safe_send_document(update, file_path)

# Start command
async def start(update: Update, context: CallbackContext) -> int:
    commands_list = (
        "Welcome👋! 🤖 I'm your CV Generator Bot. Here are the commands you can use:\n\n"
        "👉 /start👋\n"
        "👉 /help❓ \n"
        "👉 /cancel❌\n"
        "👉 /skip⏭️\n"
    )
    
    await safe_send_message(update, commands_list)
    await safe_send_message(update, "Let's get started! What is your full name? 👤🏷️")
    return NAME

async def help_command(update: Update, context: CallbackContext) -> None:
    help_text = (
        "🤖 **Available Commands:**\n\n"
        "🔹 /start👋  - Begin the CV creation process\n"
        "🔹 /help❓ - Show this help message with all commands\n"
        "🔹 /cancel❌ - Cancel the CV creation process and exit\n"
        "🔹 /skip⏭️ - Skip the current question if it's optional\n\n"
        "Use these commands anytime while interacting with me! 😊\n"
    )
    
    await safe_send_message(update, help_text)
    
# Get name
async def get_name(update: Update, context: CallbackContext) -> int:
    user_name = update.message.text.strip() 
    
    context.user_data["name"] = user_name  # Save in user_data
    
    first_name = update.message.from_user.first_name  # Get Telegram first name
    print(f"✅ Current user data: {context.user_data}")##
    await safe_send_message(update, f"Thanks, {first_name}! Now, please enter your email address📧:")
    return EMAIL

# Get email
async def get_email(update: Update, context: CallbackContext) -> int:
    email = update.message.text.strip()
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):  # Email validation
        await safe_send_message(update, "🛑Invalid email format📧! Please enter a valid email:")
        return EMAIL
    context.user_data['email'] = email
    print("✅ User Data after email entry:", context.user_data)
    await safe_send_message(update, "Please enter your phone number📞:")
    return PHONE

# Get phone number
async def get_phone(update: Update, context: CallbackContext) -> int:
    phone = update.message.text.strip()
    if not re.match(r"^\d{10}$", phone):  # Validate 10-digit phone number
        await safe_send_message(update, "🛑Invalid phone number! Please enter a 10-digit number🔢:")
        return PHONE
    context.user_data['phone'] = phone
    print("✅ User Data after phone entry:", context.user_data)
    await safe_send_message(update, "Enter your objective🎯:")
    return OBJECTIVE

# Get profile objective
async def get_objective(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.strip()
    if user_input.lower() == "/skip":
        await safe_send_message(update, "Skipping objective🎯. Now, enter your educational details🎓(Degree, Institution, Year- separated by commas):")
        return EDUCATION  # Move to next section
    context.user_data['objective'] = user_input
    await safe_send_message(update, "Required educational details🎓 (Degree, Institution, Year- separated by commas):")
    return EDUCATION

# Get education
async def get_education(update: Update, context: CallbackContext) -> int:
    education_text = update.message.text.strip()
    
    if education_text.lower() == "/skip":
        await safe_send_message(update, "Skipping education details🎓. Now, list your skills🛠️ (separated by commas):")
        return SKILLS  # Move to next section
    parts = education_text.split(',')

    if len(parts) == 3:
        try:
            start_date, end_date = parts[2].strip().split('-')
        except ValueError:  # Handles missing hyphen issue
            start_date, end_date = "Unknown", "Unknown"
        education_entry = {
            "course": parts[0].strip(),
            "institute": parts[1].strip(),
            "start_date": start_date.strip(),
            "end_date": end_date.strip(),
        }
    else:
        education_entry = {"institute": education_text}  # Fallback
        
    if "education" not in context.user_data:
            context.user_data["education"] = []

    context.user_data["education"].append(education_entry)
    await safe_send_message(update, "List your skills🛠️ (separated by commas):")
    return SKILLS

# Get skills
async def get_skills(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.strip()
    if user_input.lower() == "/skip":
        await safe_send_message(update, "Skipping skills🛠️. Now, enter your work experience🏢 (Role, Company, Start_date, End_date, Description):")
        return EXPERIENCE  # Move to next section
    
    context.user_data['skills'] = [skill.strip() for skill in update.message.text.split(',')]
    await safe_send_message(update, "Required work experience details🏢 (Role, Company, Start_date, End_date, Description):")
    return EXPERIENCE

# Get experience
async def get_experience(update: Update, context: CallbackContext) -> int:
    experience_text = update.message.text.strip()
    if experience_text.lower() == "/skip":
        await safe_send_message(update, "Skipping work experience🏢. Now, list your projects🚀 (Name, Tech, Link, Description):")
        return PROJECTS  # Move to next section
    
    parts = experience_text.split(',')

    if len(parts) == 4:
        try:
            start_date, end_date = parts[2].strip().split('-')
        except ValueError:  # Handles incorrect format
            start_date, end_date = "Unknown", "Unknown"

        experience_entry = {
            "role": parts[0].strip(),
            "company": parts[1].strip(),
            "start_date": start_date.strip(),
            "end_date": end_date.strip(),
            "description": parts[3].strip(),
        }
    else:
        experience_entry = {"role": experience_text}  # Fallback

    if "experience" not in context.user_data:
        context.user_data["experience"] = []

    context.user_data["experience"].append(experience_entry)
    await safe_send_message(update, "List any projects🚀 you have worked on (Name, Tech, Link, Description):")
    return PROJECTS

# Get projects
async def get_projects(update: Update, context: CallbackContext) -> int:
    project_text = update.message.text.strip()
    if project_text.lower() == "/skip":
        await safe_send_message(update, "Skipping projects🚀. Now, enter your volunteer experience🤝 (Role, Organization, Start_date, End_date, Description):")
        return VOLUNTEER  # Move to next section

    parts = project_text.split(',')

    if len(parts) == 4:  # Ensure all details are provided
        project_entry = {
            "name": parts[0].strip(),
            "tech": parts[1].strip(),
            "link": parts[2].strip(),
            "description": parts[3].strip()
        }
    else:
        project_entry = {"name": project_text}  # Fallback if format is incorrect

    # Store as a list of dictionaries
    if "projects" not in context.user_data:
        context.user_data["projects"] = []

    context.user_data["projects"].append(project_entry)

    await safe_send_message(update, "Enter your volunteer experience🤝 (Role, Organization, Start_date, End_date, Description):")
    return VOLUNTEER  # Move to Volunteer state

# Get volunteer experience
async def get_volunteer(update: Update, context: CallbackContext) -> int:
    volunteer_text = update.message.text.strip()
    if volunteer_text.lower() == "/skip":
        await safe_send_message(update, "Skipping volunteer experience🤝. Now, enter your achievements🏆 (separated by commas):")
        return ACHIEVEMENTS  # Move to next section
    
    parts = volunteer_text.split(',')

    if len(parts) == 4:
        duration = parts[2].strip().split('-')
        
        # Handling missing hyphen case
        if len(duration) == 2:
            start_date, end_date = duration[0], duration[1]
        else:
            start_date, end_date = "Unknown", "Unknown"

        volunteer_entry = {
            "role": parts[0].strip(),
            "organization": parts[1].strip(),
            "start_date": start_date.strip(),
            "end_date": end_date.strip(),
            "description": parts[3].strip()
        }
    else:
        volunteer_entry = {"role": volunteer_text}  # Fallback for incorrect format

    if "volunteer" not in context.user_data:
        context.user_data["volunteer"] = []

    context.user_data["volunteer"].append(volunteer_entry)

    await safe_send_message(update, "List any achievements🏆 (separated by commas):")
    return ACHIEVEMENTS  


# Get achievements
async def get_achievements(update: Update, context: CallbackContext) -> int:
    achievements_text = update.message.text.strip()
    if achievements_text.lower() == "/skip":
        await safe_send_message(update, "Skipping achievements🏆. Now, enter your LeetCode profile link🌐:")
        return LEETCODE  # Move to next section
    # Convert achievements into a list
    context.user_data["achievements"] = [ach.strip() for ach in achievements_text.split(',')]

    await safe_send_message(update, "Enter your LeetCode profile link🌐:")
    return LEETCODE  # Move to CV generation
# Validate URL function
def is_valid_url(url):
    pattern = r"^(https?:\/\/)?(www\.)?[a-zA-Z0-9._-]+\.[a-zA-Z]{2,6}(\/[^\s]*)?$"
    return re.match(pattern, url) is not None

# Get LeetCode profile link
async def get_leetcode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = update.message.text.strip()
    if url.lower() == "/skip":
        await safe_send_message(update, "Skipping LeetCode profile. Now, enter your GitHub profile link🌐:")
        return GITHUB  # Move to next section
    
    if not is_valid_url(url) or "leetcode.com" not in url:  # ✅ Corrected this line
        await safe_send_message(update, "🛑Invalid URL! Please enter a valid LeetCode profile link🌐 (e.g., https://leetcode.com/yourusername):")
        return LEETCODE  # Ask for LeetCode again if invalid

    context.user_data["leetcode"] = url
    await safe_send_message(update, "Now enter your GitHub profile link🌐:")
    
    return GITHUB  # Move to GitHub state

# Get GitHub profile link
async def get_github(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = update.message.text.strip()
    if url.lower() == "/skip":
        await safe_send_message(update, "Skipping GitHub profile🌐. Generating your CV now📄...")
        return await generate_cv(update, context)
    
    if not is_valid_url(url) or "github.com" not in url:
        await safe_send_message(update, "🛑Invalid URL! Please enter a valid GitHub profile link🌐 (e.g., https://github.com/yourusername):")
        return GITHUB  # Ask for GitHub again if invalid

    context.user_data["github"] = url
    return await generate_cv(update, context)  # Generate CV after GitHub input

# Generate CV
async def generate_cv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    clean_data = {key: value for key, value in user_data.items() if value and value != "/skip"}

    headers = {
        "Authorization": f"Bearer {MONKEY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "document": {
            "template_id": TEMPLATE_ID,
            "payload": clean_data
        }
    }

    try:
        response = requests.post(MONKEY_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        document_id = response.json().get("document", {}).get("id")

        if not document_id:
            await safe_send_message(update, "⚠️ Failed to generate CV. Please try again later.")
            return ConversationHandler.END

        # Wait and fetch the generated document
        pdf_url = None
        for _ in range(5):  # Retry 5 times
            status_response = requests.get(f"{MONKEY_API_URL}/{document_id}", headers=headers)
            if status_response.status_code == 200:
                status_data = status_response.json()
                pdf_url = status_data.get("document", {}).get("download_url")
                if pdf_url:
                    break
            await asyncio.sleep(2)  # Wait before retrying

        if pdf_url:
            await safe_send_message(update, "✅ Your CV is ready! Download it below 🖨️.")
            await safe_send_message(update, pdf_url)
        else:
            await safe_send_message(update, "⚠️ CV generation is taking too long. Try again later.")

    except requests.exceptions.RequestException as e:
        print(f"🚨 API Error: {e}")
        await safe_send_message(update, "⚠️ There was an error generating your CV. Please try again later.")

    return ConversationHandler.END


# Handle /cancel command
async def cancel(update: Update, context: CallbackContext) -> int:
    await safe_send_message(update, "CV creation cancelled❌.")
    return ConversationHandler.END

# Main function
def main():
    app = Application.builder().token(bot_token).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            OBJECTIVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_objective)],
            EDUCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_education)],
            SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_skills)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_experience)],
            PROJECTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_projects)],
            VOLUNTEER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_volunteer)],
            ACHIEVEMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_achievements)],
            LEETCODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_leetcode)],
            GITHUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_github)],
        },
        fallbacks=[CommandHandler("cancel", cancel),CommandHandler("help", help_command)],
    )
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help_command)) 
    print("Bot is running⏳...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
    
'''_________________________________________________________________________________________________
import os
import asyncio
import telegram.error 
import re
import sqlite3
import aiosqlite
from pdf_generator import generate_pdf  

import telegram.error
from dotenv import load_dotenv
from telegram import Update, InputFile, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext, ContextTypes
from database import register_user, authenticate_user, is_user_registered
import logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()
bot_token = os.getenv("BOT_TOKEN")

if not bot_token:
    raise ValueError("BOT_TOKEN is missing in the .env file")


# Define conversation states
NAME, EMAIL, PHONE, OBJECTIVE, EDUCATION, SKILLS, EXPERIENCE, PROJECTS, VOLUNTEER, ACHIEVEMENTS, LEETCODE, GITHUB, CONFIRMATION = range(13)
# Define registration states separately
(REGISTER_START, REGISTER_USERNAME, REGISTER_PASSWORD, REGISTER_NAME, REGISTER_EMAIL, 
 AUTH_USERNAME, AUTH_PASSWORD) = range(7)

# Store user data
user_data = {}

DB_FILE = "users.db"
PDF_DIR = "generated_pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

# Initialize database
def init_db():
    """Initialize the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        name TEXT,
        email TEXT,
        phone TEXT,
        experience TEXT,
        skills TEXT
    )''')

    conn.commit()
    conn.close()

init_db()

# Function to safely send messages with timeout handling
async def safe_send_message(update, text, retries=3):
    for attempt in range(retries):
        try:
            await update.message.reply_text(text)
            return  # Exit if successful
        except telegram.error.TimedOut:
            print(f"⚠️ Message timed out! Retrying ({attempt+1}/{retries}) in 5 seconds⏳...")
            await asyncio.sleep(5)
        except telegram.error.NetworkError:
            print(f"⚠️ Network error! Retrying ({attempt+1}/{retries}) in 10 seconds⏳...")
            await asyncio.sleep(10)
    print("❌ Failed to send message after retries.")

# Function to safely send documents (like PDFs)
async def safe_send_document(update, file_path, retries=3):
    for attempt in range(retries):
        try:
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    await update.message.reply_document(document=InputFile(f, filename=os.path.basename(file_path)))
            else:
                await update.message.reply_text("Error generating your CV. Please try again.")
            return  # Exit if successful
        except telegram.error.TimedOut:
            print(f"⚠️ File sending timed out! Retrying ({attempt+1}/{retries}) in 5 seconds⏳...")
            await asyncio.sleep(5)
        except telegram.error.NetworkError:
            print(f"⚠️ Network error! Retrying ({attempt+1}/{retries}) in 10 seconds⏳...")
            await asyncio.sleep(10)
    print("❌ Failed to send document after retries.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id

    async with aiosqlite.connect("users.db") as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = await cursor.fetchone()

    if user:
        await update.message.reply_text(
            "😊👋 Welcome back! You are already registered. Here are the available commands:\n"
            "👉 /start👋\n"
            "👉 /register📝 \n"
            "👉 /login🔑 \n"
            "👉 /help❓ \n"
            "👉 /cancel❌\n"
            "👉 /skip⏭️\n"
            "👉 /create_cv📝 \n"
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "😊👋 Welcome to the CV Generator Bot🤖! Here are the available commands:\n"
            "👉 /start👋\n"
            "👉 /register📝 \n"
            "👉 /login🔑 \n"
            "👉 /help❓\n"
            "👉 /cancel❌\n"
            "👉 /skip⏭️\n"
            "👉 /create_cv📝 \n"
        )
        return await register_start(update, context)
    
async def help_command(update: Update, context: CallbackContext) -> None:
    help_text = (
    "🤖 **Available Commands:**\n\n"
    "🔹 /start👋  - Begin the CV creation process\n"
    "🔹 /register - Create an account 🆕\n"
    "🔹 /login - Log in to your account 🔑\n"
    "🔹 /help❓ - Show this help message with all commands\n"
    "🔹/create_cv 📝 - Start creating your CV\n"
    "🔹 /cancel❌ - Cancel the CV creation process and exit\n"
    "🔹 /skip⏭️ - Skip the current question if it's optional\n\n"
    "Use these commands anytime while interacting with me! 😊\n"
    )

    await safe_send_message(update, help_text)

# Registration process
async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Let's get started the registration process!🚀\n 👤Enter your username:")
    return REGISTER_USERNAME

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text.strip()

    # ✅ Corrected: Check BEFORE saving in context.user_data
    if not username:
        await update.message.reply_text("⚠️ Username cannot be empty. Please enter a valid username:")
        return REGISTER_USERNAME  

    # ✅ Store username
    context.user_data["username"] = username  

    # ✅ Debug message in chat
    await update.message.reply_text(f"DEBUG: Received username {username}")  

    # ✅ Write debug info to a log file
    with open("debug.log", "a") as log_file:
        log_file.write(f"📌 DEBUG: Received username: {username}\n")
        log_file.flush()  # ✅ Ensure immediate writing to file  

    # ✅ Proceed to next step: Ask for password
    await update.message.reply_text("Now enter a password🔑 (minimum 6 characters):")
    return REGISTER_PASSWORD  

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    password = update.message.text.strip()
    if len(password) < 6:
        await update.message.reply_text("❌ Password too short! Enter at least 6 characters:")
        return REGISTER_PASSWORD

    username = context.user_data["username"]
    user_id = update.message.from_user.id

    async with aiosqlite.connect("users.db") as conn:
        await conn.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password)
        )
        await conn.commit()
        await conn.close()

    await update.message.reply_text("✅ Registration successful! You can now /login.")
    context.user_data["password"] = update.message.text
    update.message.reply_text("Now, please enter your username name:")
    return REGISTER_NAME  # Moving to the name state

async def register_name(update: Update, context: CallbackContext) -> int:
    context.user_data["name"] = update.message.text
    await safe_send_message(update, "Finally, enter your email address:")
    return REGISTER_EMAIL  # Moving to the email state

# Function to handle email input
async def register_email(update: Update, context: CallbackContext) -> int:
    context.user_data["email"] = update.message.text
    # Confirming the details
    update.message.reply_text(
        f"✅ Thank you for registering!\n\n"
        f"📌 Username: {context.user_data['username']}\n"
        f"👤 Name: {context.user_data['name']}\n"
        f"📧 Email: {context.user_data['email']}\n\n"
        "🎉 Now let's create your CV! 🚀"
    )

    return await create_cv(update, context)

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Enter your username:")
    return AUTH_USERNAME

async def auth_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["auth_username"] = update.message.text.strip()
    await update.message.reply_text("Now enter your password:")
    return AUTH_PASSWORD

async def auth_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = context.user_data["auth_username"]
    password = update.message.text.strip()

    async with aiosqlite.connect("users.db") as conn:
        async with aiosqlite.connect("users.db") as conn:
            async with conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?", (username, password)
            ) as cursor:
                user = await cursor.fetchone()

    if user:
        await safe_send_message(update, "✅ Login successful! You can now create your CV.")
    else:
        await update.message.reply_text("❌ Incorrect username or password. Try again with /login.")
    
    return ConversationHandler.END
 
 
async def create_cv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the CV creation process."""
    await update.message.reply_text("Let's build your CV! 📝\nWhat is your full name?")
    return NAME  # Moves to get_name()

    
# Get name
async def get_name(update: Update, context: CallbackContext) -> int:
    user_name = update.message.text.strip() 
    
    context.user_data["name"] = user_name  # Save in user_data
    
    first_name = update.message.from_user.first_name  # Get Telegram first name
    print(f"✅ Current user data: {context.user_data}")##
    await safe_send_message(update, f"Thanks, {first_name}! Now, please enter your email address📧:")
    return EMAIL

# Get email
async def get_email(update: Update, context: CallbackContext) -> int:
    email = update.message.text.strip()
    
    # Email validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        await safe_send_message(update, "🛑 Invalid email format 📧! Please enter a valid email:")
        return EMAIL

    user_id = update.message.from_user.id
    name = context.user_data.get('name', None)
    username = context.user_data.get('username', None)  # ✅ Retrieve username
    
    if not name or not username:
        await safe_send_message(update, "❌ Error: Name or Username is missing. Restart the process with registration.")
        return ConversationHandler.END

    context.user_data['email'] = email  # Store in user_data for later use
     
    # Store in SQLite database
    async with aiosqlite.connect("users.db") as conn:
        await conn.execute("INSERT INTO users (id, name, email) VALUES (?, ?, ?)", (user_id, name, email))
        await conn.commit()
        conn.close()

    print("✅ User Data after email entry:", context.user_data)

    # Ask for the phone number next
    await safe_send_message(update, "Please enter your phone number 📞:")
    return PHONE  # Move to the phone number state in the conversation flow

# Get phone number
async def get_phone(update: Update, context: CallbackContext) -> int:
    phone = update.message.text.strip()
    if not re.match(r"^\d{10}$", phone):  # Validate 10-digit phone number
        await safe_send_message(update, "🛑Invalid phone number! Please enter a 10-digit number🔢:")
        return PHONE
    context.user_data['phone'] = phone
    print("✅ User Data after phone entry:", context.user_data)
    await safe_send_message(update, "Enter your objective🎯:")
    return OBJECTIVE

# Get profile objective
async def get_objective(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.strip()
    if user_input.lower() == "/skip":
        await safe_send_message(update, "Skipping objective🎯. Now, enter your educational details🎓(Degree, Institution, Year- separated by commas):")
        return EDUCATION  # Move to next section
    context.user_data['objective'] = user_input
    await safe_send_message(update, "Required educational details🎓 (Degree, Institution, Year- separated by commas):")
    return EDUCATION

# Get education
async def get_education(update: Update, context: CallbackContext) -> int:
    education_text = update.message.text.strip()
    
    if education_text.lower() == "/skip":
        await safe_send_message(update, "Skipping education details🎓. Now, list your skills🛠️ (separated by commas):")
        return SKILLS  # Move to next section
    parts = education_text.split(',')

    if len(parts) == 3:
        try:
            start_date, end_date = parts[2].strip().split('-')
        except ValueError:  # Handles missing hyphen issue
            start_date, end_date = "Unknown", "Unknown"
        education_entry = {
            "course": parts[0].strip(),
            "institute": parts[1].strip(),
            "start_date": start_date.strip(),
            "end_date": end_date.strip(),
        }
    else:
        education_entry = {"institute": education_text}  # Fallback
        
    if "education" not in context.user_data:
            context.user_data["education"] = []

    context.user_data["education"].append(education_entry)
    await safe_send_message(update, "List your skills🛠️ (separated by commas):")
    return SKILLS

# Get skills
async def get_skills(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.strip()
    if user_input.lower() == "/skip":
        await safe_send_message(update, "Skipping skills🛠️. Now, enter your work experience🏢 (Role, Company, Start_date, End_date, Description):")
        return EXPERIENCE  # Move to next section
    
    context.user_data['skills'] = [skill.strip() for skill in update.message.text.split(',')]
    await safe_send_message(update, "Required work experience details🏢 (Role, Company, Start_date, End_date, Description):")
    return EXPERIENCE

# Get experience
async def get_experience(update: Update, context: CallbackContext) -> int:
    experience_text = update.message.text.strip()
    if experience_text.lower() == "/skip":
        await safe_send_message(update, "Skipping work experience🏢. Now, list your projects🚀 (Name, Tech, Link, Description):")
        return PROJECTS  # Move to next section
    
    parts = experience_text.split(',')

    if len(parts) == 4:
        try:
            start_date, end_date = parts[2].strip().split('-')
        except ValueError:  # Handles incorrect format
            start_date, end_date = "Unknown", "Unknown"

        experience_entry = {
            "role": parts[0].strip(),
            "company": parts[1].strip(),
            "start_date": start_date.strip(),
            "end_date": end_date.strip(),
            "description": parts[3].strip(),
        }
    else:
        experience_entry = {"role": experience_text}  # Fallback

    if "experience" not in context.user_data:
        context.user_data["experience"] = []

    context.user_data["experience"].append(experience_entry)
    await safe_send_message(update, "List any projects🚀 you have worked on (Name, Tech, Link, Description):")
    return PROJECTS

# Get projects
async def get_projects(update: Update, context: CallbackContext) -> int:
    project_text = update.message.text.strip()
    if project_text.lower() == "/skip":
        await safe_send_message(update, "Skipping projects🚀. Now, enter your volunteer experience🤝 (Role, Organization, Start_date, End_date, Description):")
        return VOLUNTEER  # Move to next section

    parts = project_text.split(',')

    if len(parts) == 4:  # Ensure all details are provided
        project_entry = {
            "name": parts[0].strip(),
            "tech": parts[1].strip(),
            "link": parts[2].strip(),
            "description": parts[3].strip()
        }
    else:
        project_entry = {"name": project_text}  # Fallback if format is incorrect

    # Store as a list of dictionaries
    if "projects" not in context.user_data:
        context.user_data["projects"] = []

    context.user_data["projects"].append(project_entry)

    await safe_send_message(update, "Enter your volunteer experience🤝 (Role, Organization, Start_date, End_date, Description):")
    return VOLUNTEER  # Move to Volunteer state

# Get volunteer experience
async def get_volunteer(update: Update, context: CallbackContext) -> int:
    volunteer_text = update.message.text.strip()
    if volunteer_text.lower() == "/skip":
        await safe_send_message(update, "Skipping volunteer experience🤝. Now, enter your achievements🏆 (separated by commas):")
        return ACHIEVEMENTS  # Move to next section
    
    parts = volunteer_text.split(',')

    if len(parts) == 4:
        duration = parts[2].strip().split('-')
        
        # Handling missing hyphen case
        if len(duration) == 2:
            start_date, end_date = duration[0], duration[1]
        else:
            start_date, end_date = "Unknown", "Unknown"

        volunteer_entry = {
            "role": parts[0].strip(),
            "organization": parts[1].strip(),
            "start_date": start_date.strip(),
            "end_date": end_date.strip(),
            "description": parts[3].strip()
        }
    else:
        volunteer_entry = {"role": volunteer_text}  # Fallback for incorrect format

    if "volunteer" not in context.user_data:
        context.user_data["volunteer"] = []

    context.user_data["volunteer"].append(volunteer_entry)

    await safe_send_message(update, "List any achievements🏆 (separated by commas):")
    return ACHIEVEMENTS  


# Get achievements
async def get_achievements(update: Update, context: CallbackContext) -> int:
    achievements_text = update.message.text.strip()
    if achievements_text.lower() == "/skip":
        await safe_send_message(update, "Skipping achievements🏆. Now, enter your LeetCode profile link🌐:")
        return LEETCODE  # Move to next section
    # Convert achievements into a list
    context.user_data["achievements"] = [ach.strip() for ach in achievements_text.split(',')]

    await safe_send_message(update, "Enter your LeetCode profile link🌐:")
    return LEETCODE  # Move to CV generation

# Validate URL function
def is_valid_url(url):
    pattern = r"^(https?:\/\/)?(www\.)?[a-zA-Z0-9._-]+\.[a-zA-Z]{2,6}(\/[^\s]*)?$"
    return re.match(pattern, url) is not None

# Get LeetCode profile link
async def get_leetcode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = update.message.text.strip()
    if url.lower() == "/skip":
        await safe_send_message(update, "Skipping LeetCode profile. Now, enter your GitHub profile link🌐:")
        return GITHUB  # Move to next section
    
    if not is_valid_url(url) or "leetcode.com" not in url:  # ✅ Corrected this line
        await safe_send_message(update, "🛑Invalid URL! Please enter a valid LeetCode profile link🌐 (e.g., https://leetcode.com/yourusername):")
        return LEETCODE  # Ask for LeetCode again if invalid

    context.user_data["leetcode"] = url
    await safe_send_message(update, "Now enter your GitHub profile link🌐:")
    
    return GITHUB  # Move to GitHub state

# Get GitHub profile link
async def get_github(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = update.message.text.strip()
    
    user_details = f"Name: {context.user_data['name']}\nEmail: {context.user_data['email']}\nPhone: {context.user_data['phone']}\nExperience: {context.user_data['experience']}\nSkills: {context.user_data['skills']}"
    
    await safe_send_message(update, "Skipping GitHub profile🌐")
    
    if url.lower() == "/skip":
        await update.message.reply_text(f"Please confirm your details:\n{user_details}\nType 'yes' to confirm or 'no' to restart.")
        return CONFIRMATION
    
    if not is_valid_url(url) or "github.com" not in url:
        await safe_send_message(update, "🛑Invalid URL! Please enter a valid GitHub profile link🌐 (e.g., https://github.com/yourusername):")
        return GITHUB  # Ask for GitHub again if invalid

    context.user_data["github"] = url
    return CONFIRMATION  # Generate CV after GitHub input

async def confirm_details(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() == 'yes':
        # Save user to DB
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, phone, experience, skills) VALUES (?, ?, ?, ?, ?)",
                       (context.user_data['name'], context.user_data['email'], context.user_data['phone'], context.user_data['experience'], context.user_data['skills']))
        conn.commit()
        conn.close()
        
        await update.message.reply_text("Your details have been saved! Generating your CV...")
        return await generate_cv(update, context)
    else:
        await update.message.reply_text("Let's start over. What's your name?")
        return await generate_cv(update, context)
    
# Generate CV
async def generate_cv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    
    clean_data = {key: value for key, value in user_data.items() if value and value != "/skip"}
    
    pdf_path = generate_pdf(clean_data)

    if not pdf_path:
        await safe_send_message(update, "❌ Failed to generate your CV. Please try again later.")
        return ConversationHandler.END

    await safe_send_message(update, "✅ Your CV is ready! Download it below 🖨️.")
    await safe_send_document(update, pdf_path)

    return ConversationHandler.END

# Handle /cancel command
async def cancel(update: Update, context: CallbackContext) -> int:
    await safe_send_message(update, "CV creation cancelled❌.")
    await update.message.reply_text(" Operation canceled. You can start again with /start.")
    return ConversationHandler.END

def main():
    init_db()
    app = Application.builder().token(bot_token).build()

    # Registration Handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register', register_start)],
        states={
            REGISTER_START: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_start)],
            REGISTER_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            REGISTER_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            REGISTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_name)],
            REGISTER_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_email)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Login Handler
    login_handler = ConversationHandler(
        entry_points=[CommandHandler("login", login)],
        states={
            AUTH_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth_username)],
            AUTH_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # CV Creation Handler (Unified)
    cv_handler = ConversationHandler(
        entry_points=[CommandHandler("create_cv", create_cv)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            OBJECTIVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_objective)],
            EDUCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_education)],
            SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_skills)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_experience)],
            PROJECTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_projects)],
            VOLUNTEER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_volunteer)],
            ACHIEVEMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_achievements)],
            LEETCODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_leetcode)],
            GITHUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_github)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("help", help_command)],
    )

    # Add handlers to the bot
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("register", register_start))
    app.add_handler(conv_handler)
    app.add_handler(login_handler)
    app.add_handler(cv_handler)
    app.add_handler(CommandHandler("cancel", cancel))  


    print("Bot is running ⏳...")
    app.run_polling()

if __name__ == "__main__":
    main()
'''
