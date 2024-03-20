from typing import Final
import os
import discord
import asyncio
from dotenv import load_dotenv
from discord import Intents, Client, Message, Guild, Member
from responses import get_response
from datetime import datetime
import random
import csv

# STEP 0: LOAD OUR TOKEN FROM SOMEWHERE SAFE
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Load suspicious words from file
with open("sus.txt", "r") as file:
    SUSPICIOUS_WORDS = file.read().splitlines()

# Dictionary to store user XP
user_xp = {}

# Load user XP from file if available
if os.path.exists("user_xp.csv"):
    with open("user_xp.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            user_xp[row[0]] = int(row[1])

# Function to save user XP to file
def save_user_xp():
    with open("user_xp.csv", "w", newline='') as file:
        writer = csv.writer(file)
        for user, xp in user_xp.items():
            writer.writerow([user, xp])

# Function to calculate level from XP
def calculate_level(xp):
    level = 0
    while xp >= calculate_xp_required(level + 1):
        level += 1
    return level

# Function to calculate XP required for a level
def calculate_xp_required(level):
    return 5 * (level ** 2) + (50 * level) + 100

# Function to update ranks file
def update_ranks():
    ranks_data = []
    for member_id, xp in user_xp.items():
        level = calculate_level(xp)
        ranks_data.append([client.get_user(int(member_id)), level, xp])
    with open("ranks.txt", "w") as ranks_file:
        writer = csv.writer(ranks_file)
        writer.writerow(["Name", "Level", "XP"])
        writer.writerows(ranks_data)

# Function to handle XP gain from messages
async def handle_xp(message):
    author_id = str(message.author.id)
    user_xp[author_id] = user_xp.get(author_id, 0) + 1
    save_user_xp()

# STEP 1: BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)

# STEP 2: MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

# STEP 3: KICK COMMAND
async def kick_member(guild: Guild, member: Member, reason: str) -> None:
    await member.kick(reason=reason)

# STEP 4: BAN COMMAND
async def ban_member(guild: Guild, member: Member, reason: str) -> None:
    await member.ban(reason=reason)

# STEP 5: HANDLING THE STARTUP FOR OUR BOT
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')

# STEP 6: HANDLING INCOMING MESSAGES
async def handle_xp(message):
    author_id = str(message.author.id)
    xp_gain = random.randint(1, 10)
    user_xp[author_id] = user_xp.get(author_id, 0) + xp_gain
    save_user_xp()

@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    # Check if it's the !level command
    if message.content.startswith('!level'):
        author_id = str(message.author.id)
        xp = user_xp.get(author_id, 0)
        level = calculate_level(xp)
        await message.channel.send(f"{message.author} is at level {level} with {xp} XP.")

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    with open("log.txt", "a") as log_file:
        log_file.write(f"[{datetime.now()}] [{channel}] {username}: {user_message}\n")

    print(f'[{channel}] {username}: "{user_message}"')

    # Handle XP gain
    await handle_xp(message)

    # Check if the message contains any suspicious words
    if any(word.lower() in user_message.lower() for word in SUSPICIOUS_WORDS):
        # Delete the message
        await message.delete()
        await message.channel.send(f"Message from {username} containing suspicious content has been deleted.")

        # Mute the offender for 5 minutes
        await message.author.add_roles(discord.utils.get(message.guild.roles, name="Muted"))

        # Unmute the offender after 5 minutes
        await asyncio.sleep(10)  # 300 seconds = 5 minutes
        await message.channel.send(f"Dummy has been unmuted")
        await message.author.remove_roles(discord.utils.get(message.guild.roles, name="Muted"))

    # Split the user's message to get the command and arguments
    parts = user_message.split(' ')
    command = parts[0].lower()
    arguments = parts[1:]

    if command == '!kick':
        if not message.author.guild_permissions.kick_members:
            await message.channel.send("You don't have permission to kick members.")
            return

        # Check if any member ID is provided
        if not arguments:
            await message.channel.send("Please provide a member ID to kick.")
            return

        member_id = int(arguments[0])  # Convert the member ID to int
        try:
            member = await message.guild.fetch_member(member_id)
            await member.kick(reason=' '.join(arguments[1:]) or 'No reason provided.')
            await message.channel.send(f"Kicked {member.display_name} from the server.")
        except discord.errors.NotFound:
            await message.channel.send("Member not found.")
        except discord.errors.Forbidden:
            await message.channel.send("I don't have permission to kick that member.")

    elif command == '!ban':
        if not message.author.guild_permissions.ban_members:
            await message.channel.send("You don't have permission to ban members.")
            return

        # Check if any member ID is provided
        if not arguments:
            await message.channel.send("Please provide a member ID to ban.")
            return

        member_id = int(arguments[0])  # Convert the member ID to int
        try:
            member = await message.guild.fetch_member(member_id)
            await member.ban(reason=' '.join(arguments[1:]) or 'No reason provided.')
            await message.channel.send(f"Banned {member.display_name} from the server.")
        except discord.errors.NotFound:
            await message.channel.send("Member not found.")
        except discord.errors.Forbidden:
            await message.channel.send("I don't have permission to ban that member.")

    else:
        await send_message(message, user_message)

    # Update ranks file after each message
    update_ranks()


# STEP 7: MAIN ENTRY POINT
def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()
