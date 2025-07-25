from keep_alive import keep_alive
keep_alive()

import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io
import random
import aiohttp
import os
from dotenv import load_dotenv

# Tải biến môi trường từ .env
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Khởi tạo bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Khi bot sẵn sàng
@bot.event
async def on_ready():
    print(f'✅ Bot đã đăng nhập thành {bot.user}')

# Hàm tải avatar
async def fetch_avatar(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            data = await resp.read()
            return Image.open(io.BytesIO(data)).convert("RGBA")

# Lệnh love
@bot.command()
async def love(ctx, member1: discord.Member = None, member2: discord.Member = None):
    if member1 is None and member2 is None:
        await ctx.send("Bạn cần tag ít nhất 1 người.")
        return

    if member2 is None:
        member2 = member1
        member1 = ctx.author

    if member1.id == member2.id:
        await ctx.send("Bạn cần tag 2 người khác nhau!")
        return

    avatar1 = await fetch_avatar(member1.display_avatar.url)
    avatar2 = await fetch_avatar(member2.display_avatar.url)
    heart = Image.open("heart.png").convert("RGBA")

    if not avatar1 or not avatar2:
        await ctx.send("Không thể tải avatar.")
        return

    avatar1 = avatar1.resize((150, 150))
    avatar2 = avatar2.resize((150, 150))
    heart = heart.resize((100, 100))

    final_img = Image.new("RGBA", (420, 160), (0, 0, 0, 0))
    final_img.paste(avatar1, (0, 5))
    final_img.paste(heart, (160, 30), heart)
    final_img.paste(avatar2, (270, 5))

    buffer = io.BytesIO()
    final_img.save(buffer, format="PNG")
    buffer.seek(0)

    percent = random.randint(0, 100)
    if percent < 5:
        msg = "Đừng bao giờ... bao giờ nghĩ tới chuyện này 🤢🤮"
    elif percent < 10:
        msg = "Một thảm họa tình cảm 😰"
    elif percent < 20:
        msg = "Cút đi 😤"
    elif percent < 30:
        msg = "Bạn bè thôi 💔"
    elif percent < 50:
        msg = "Chưa đủ lửa, chưa đủ duyên đâu🤪"
    elif percent < 70:
        msg = "Có thể sẽ là một đôi tạm ổn 💛"
    elif percent < 80:
        msg = "Tình yêu đang nảy mầm rồi đấy ❤️"
    elif percent < 100:
        msg = "Tình yêu đích thực!!! 💘"
    else:
        msg = "Sinh ra là để dành cho nhau 💍"

    embed = discord.Embed(
        title=f"{member1.display_name} ❤️ {member2.display_name} = {percent}%",
        description=msg,
        color=discord.Color.pink()
    )
    file = discord.File(buffer, filename="love.png")
    embed.set_image(url="attachment://love.png")
    await ctx.send(file=file, embed=embed)

# Lệnh gayrate
@bot.command()
async def gayrate(ctx, member: discord.Member = None):
    member = member or ctx.author
    percent = random.randint(0, 100)

    if percent < 5:
        msg = "Chắc chắn không gay… trừ khi đang giấu 🤨"
    elif percent < 10:
        msg = "Hmmm... có vẻ thẳng đấy, nhưng ai mà biết được 👀"
    elif percent < 20:
        msg = "Thẳng tới mức đáng nghi 😶"
    elif percent < 30:
        msg = "Chưa hẳn là gay… nhưng cũng chưa chắc 🧐"
    elif percent < 50:
        msg = "Bê đê hả 😏"
    elif percent < 70:
        msg = "Gay to 🌈"
    elif percent < 85:
        msg = "Chắc là gay đấy, đừng chối 😂"
    elif percent < 100:
        msg = "Ôi trời ơi, quá là gay luôn 🌈🔥"
    else:
        msg = "Xin lỗi nhưng bạn là gay chính hiệu rồi 🏳️‍🌈💅"

    embed = discord.Embed(
        title=f"{member.display_name} là {percent}% gay!",
        description=msg,
        color=discord.Color.random()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

# Chạy bot
if not TOKEN:
    print("❌ Không tìm thấy token trong file .env")
else:
    bot.run(TOKEN)












