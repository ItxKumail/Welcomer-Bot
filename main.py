import discord
import os
import requests
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

TOKEN = os.getenv("BOT_TOKEN")
WELCOME_CHANNEL_ID = 1395650553878544414
BACKGROUND_URL = "https://i.postimg.cc/m2wvxLYw/7065e23d412b3ff3dc242d19ab4b4a57.jpg"

intents = discord.Intents.default()
intents.members = True           # For on_member_join
intents.message_content = True  # For reading message content
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    # Load background image
    bg_response = requests.get(BACKGROUND_URL)
    bg_image = Image.open(BytesIO(bg_response.content)).convert("RGBA")
    bg_image = bg_image.resize((800, 250))  # Adjust as needed

    # Create dark overlay (semi-transparent black)
    overlay = Image.new("RGBA", bg_image.size, (0, 0, 0, 60))  # Alpha 120 = ~50% darkness
    bg_image = Image.alpha_composite(bg_image, overlay)

    # Load and crop avatar
    avatar_response = requests.get(member.avatar.url)
    avatar_image = Image.open(BytesIO(avatar_response.content)).convert("RGBA")
    avatar_image = avatar_image.resize((128, 128))

    # Make avatar circular
    mask = Image.new("L", avatar_image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, 128, 128), fill=255)
    avatar_image.putalpha(mask)

    # Paste avatar on background
    bg_image.paste(avatar_image, (30, 60), avatar_image)

    # Add welcome text
    draw = ImageDraw.Draw(bg_image)

    font_path = "fonts/Montserrat-Bold.ttf"

    font = ImageFont.truetype(font_path, size=16)
    
    # Shadow settings
    text_position = (100, 100)
    shadow_color = (0, 0, 0)
    shadow_offset = (2, 2)
    # Draw shadow (first)
    draw.text(
    (text_position(100, 100) + shadow_offset[0], text_position[1] + shadow_offset[1]),
    welcome_text,
    font=font,
    fill=shadow_color
    )

    welcome_text = f"Welcome, {member.display_name}!\nPlease verify in #verify to access the rest of the server."
    draw.text((180, 100), welcome_text, font=font, fill=(255, 255, 255))

    # Save to buffer
    buffer = BytesIO()
    bg_image.save(buffer, format="PNG")
    buffer.seek(0)

    # Send the final image
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(file=discord.File(buffer, "welcome.png"))

@bot.command()
async def testwelcome(ctx):
    await on_member_join(ctx.author)

bot.run(TOKEN)
