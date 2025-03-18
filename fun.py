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
bot_token = os.getenv("BOT_TOKEN")

if not bot_token:
    raise ValueError("BOT_TOKEN is missing in the .env file")

# Define conversation states
NAME, EMAIL, PHONE, OBJECTIVE, EDUCATION, SKILLS, EXPERIENCE, PROJECTS, VOLUNTEER, ACHIEVEMENTS, LEETCODE, GITHUB = range(12)

# Store user data
user_data = {}

# Function to safely send messages with timeout handling
async def safe_send_message(update, text):
    try:
        await update.message.reply_text(text)
        await asyncio.sleep(0.5)  # Prevents spam blocking
    except telegram.error.TimedOut:
        print("⚠️Message timed out! Retrying in 5 seconds⏳...")
        await asyncio.sleep(5)
        await safe_send_message(update, text)  # Retry sending
    except telegram.error.NetworkError:
        print("⚠️Network error! Retrying in 10 seconds⏳...")
        await asyncio.sleep(10)
        await safe_send_message(update, text)

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
    
    pdf_path = generate_pdf(clean_data)

    await safe_send_message(update, "✅ Your CV is ready! Download it below 🖨️.")
    await safe_send_document(update, pdf_path)

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