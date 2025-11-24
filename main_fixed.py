import os
import logging
import discord
from discord.ext import commands
import asyncio

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

load_dotenv()

TOKEN_LIST = os.getenv("TOKEN_LIST")
if TOKEN_LIST is None:
    raise ValueError("No TOKEN_LIST found. Please set TOKEN_LIST in .env file.")
TOKEN_LIST = TOKEN_LIST.split(",")
DEFAULT_DELAY = int(os.getenv("DEFAULT_DELAY", 3))

ALLOWED_USER_ID = 966285343441715200
prefix = "."

bot = commands.Bot(command_prefix=prefix, help_command=None, case_insensitive=True)

# Loop state
giet_running = False
giet_task = None
treo_running = False
treo_task = None
stop_flag = False

# Small example messages list (replace/extend as you like)
messages = [
    "# Message A",
    "# Message B",
    "# Message C",
]


@bot.check
def only_me_in_guild(ctx):
    return ctx.guild is not None and ctx.author.id == ALLOWED_USER_ID


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return
    if isinstance(error, commands.CommandNotFound):
        return
    raise error


@bot.command()
async def hey(ctx):
    await ctx.send("Gì em")


@bot.command()
async def treo(ctx):
    global treo_running, treo_task
    if treo_running:
        await ctx.send("🔴 Treo đang chạy rồi!", delete_after=1)
        return
    treo_running = True
    # Read content to spam from treo.txt
    try:
        with open("treo.txt", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        await ctx.send("⚠️ Không tìm thấy file `treo.txt`. Vui lòng tạo file này chứa nội dung cần treo.", delete_after=5)
        treo_running = False
        return
    except Exception as e:
        await ctx.send(f"❌ Lỗi khi đọc file `treo.txt`: {e}", delete_after=5)
        treo_running = False
        return

    content = content.strip()
    if not content:
        await ctx.send("⚠️ File `treo.txt` rỗng. Vui lòng thêm nội dung để treo.", delete_after=5)
        treo_running = False
        return

    async def loop_treo():
        backoff = 1.0
        delay = getattr(ctx.bot, "DEFAULT_DELAY", 3)
        while treo_running:
            try:
                await ctx.send(content)
                backoff = 1.0
            except discord.HTTPException:
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)
            await asyncio.sleep(delay)

    treo_task = asyncio.create_task(loop_treo())


@bot.command()
async def giet(ctx, *members: discord.Member):
    global giet_running, giet_task
    if giet_running:
        await ctx.send("🔴 Giet đang chạy rồi!", delete_after=1)
        return
    if not members:
        await ctx.send("⚠️ Bạn cần tag ít nhất 1 người để 'giet'!", delete_after=1)
        return

    # Try to read lines from giet.txt
    try:
        with open("giet.txt", "r", encoding="utf-8") as f:
            raw_lines = f.readlines()
    except FileNotFoundError:
        await ctx.send("⚠️ Không tìm thấy file `giet.txt`. Vui lòng tạo file này chứa các dòng tin nhắn để gieo.", delete_after=5)
        return
    except Exception as e:
        await ctx.send(f"❌ Lỗi khi đọc file `giet.txt`: {e}", delete_after=5)
        return

    # Normalize and filter out empty lines
    lines = [ln.rstrip("\n") for ln in raw_lines]
    # remove fully-empty lines
    lines = [ln for ln in lines if ln.strip()]

    if not lines:
        await ctx.send("⚠️ File `giet.txt` rỗng. Vui lòng thêm các dòng tin nhắn.", delete_after=5)
        return

    giet_running = True

    async def loop_giet():
        mentions = " ".join([m.mention for m in members])
        try:
            await ctx.send(f"😈 Bắt đầu gieo rắc nỗi đau cho {mentions}!", delete_after=1)
        except discord.HTTPException:
            pass

        backoff = 1.0
        delay = getattr(ctx.bot, "DEFAULT_DELAY", 3)
        idx = 0
        n = len(lines)
        while giet_running:
            if not giet_running:
                break
            msg = lines[idx]
            try:
                await ctx.send(f"{msg} {mentions}" if mentions else msg)
                backoff = 1.0
            except discord.HTTPException:
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)
            await asyncio.sleep(delay)
            idx = (idx + 1) % n

    giet_task = asyncio.create_task(loop_giet())


@bot.command()
async def dung(ctx):
    """Unified stop: stops giet, treo, and nhay loops/tasks."""
    global giet_running, giet_task, treo_running, treo_task, stop_flag
    stopped_any = False

    if giet_running:
        giet_running = False
        stopped_any = True

    if treo_running:
        treo_running = False
        stopped_any = True

    if not stop_flag:
        stop_flag = True
        stopped_any = True

    cancel_tasks = []
    if giet_task:
        cancel_tasks.append(("giet", giet_task))
    if treo_task:
        cancel_tasks.append(("treo", treo_task))

    for name, task in cancel_tasks:
        try:
            task.cancel()
        except Exception:
            pass

    for name, task in cancel_tasks:
        try:
            await asyncio.wait_for(task, timeout=2)
        except Exception:
            pass

    giet_task = None
    treo_task = None

    if stopped_any:
        await ctx.send("🔴 Đã dừng tất cả tác vụ.", delete_after=2)
    else:
        await ctx.send("⚪ Không có tác vụ nào đang chạy.", delete_after=2)


@bot.command()
async def tag(ctx, member: discord.Member):
    DELETE_AFTER = 2
    TIMES = 5

    for i in range(TIMES):
        try:
            await ctx.send(f"{member.mention}", delete_after=DELETE_AFTER)
            await asyncio.sleep(2)
        except Exception:
            pass


@bot.command()
async def nhay(ctx, *members: discord.Member):
    """
    Gửi các dòng trong nhay.txt kèm ping các member được tag.
    Cú pháp: .nhay @user1 @user2
    """
    global stop_flag
    stop_flag = False

    try:
        with open("nhay.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            await ctx.send("📂 File trống hoặc không tìm thấy nội dung nào.", delete_after=0.3)
            return

        mentions = " ".join([m.mention for m in members]) if members else ""

        await ctx.send(f"🎉 Bắt đầu nhảy tin nhắn! {mentions}", delete_after=0.3)

        backoff = 1.0
        delay = getattr(ctx.bot, "DEFAULT_DELAY", 3)
        for line in lines:
            if stop_flag:
                await ctx.send("Đã dừng", delete_after=0.3)
                break

            text = line.strip()
            if text:
                msg_to_send = f"{text} {mentions}" if mentions else text
                try:
                    await ctx.send(msg_to_send)
                    backoff = 1.0
                except discord.HTTPException:
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, 60)
                await asyncio.sleep(delay)

    except FileNotFoundError:
        await ctx.send("⚠️ Không tìm thấy file `nhay.txt` trong thư mục bot.", delete_after=0.5)
    except Exception as e:
        await ctx.send(f"❌ Lỗi: {e}", delete_after=0.3)


@bot.event
async def on_message(message: discord.Message):
    """Only allow this bot to process messages from the configured user.

    - Ignore other authors (return early).
    - If message.content == ".hey" respond with "Gì!!!".
    - For allowed messages, continue to process commands as well.
    """
    # ignore messages from bots
    if message.author is None or getattr(message.author, "bot", False):
        return

    # Only allow messages from the owner user
    if message.author.id != ALLOWED_USER_ID:
        return

    # simple direct-text handler
    if message.content == ".hey":
        await message.channel.send("Gì!!!")
        return

    # allow normal command processing for allowed messages
    await bot.process_commands(message)


@bot.event
async def on_ready():
    logging.basicConfig(level=logging.INFO)
    print(f"✅ Bot ready: {bot.user}")

    # default delay for looped messages (seconds)
    bot.DEFAULT_DELAY = int(os.environ.get("DEFAULT_DELAY", "3"))


def _get_token():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("Bot token not set. Please set DISCORD_TOKEN environment variable.")
    return token


if __name__ == "__main__":
    try:
        TOKEN = _get_token()
        bot.run(TOKEN)
    except Exception as e:
        print(f"Fatal: {e}")
