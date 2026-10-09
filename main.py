import ipaddress
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import discord
from discord.ext import commands

# ڕێکخستنی پێویست بۆ بۆتەکە
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.command(name="ip")
async def locate_ip(ctx, ip: str):
    ip = ip.strip()

    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        await ctx.send("❌ ناونیشانی IPـیەکەی هەڵەیە.")
        return

    if not address.is_global:
        await ctx.send("⚠️ ئەمە IPـیەکی گشتی (Public) نییە.")
        return

    url = f"https://ipwho.is/{ip}"
    request = Request(
        url,
        headers={"User-Agent": "CyberSecurityToolkit/1.0"}
    )

    try:
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        if not data.get("success", False):
            await ctx.send(f"❌ نەتوانرا زانیاری دەربهێنرێت: {data.get('message', 'هەڵەیەکی نەزانراو')}")
            return

        connection = data.get("connection") or {}
        timezone = data.get("timezone") or {}

        # دروستکردنی شێوازێکی جوان بۆ نیشاندان لە دیسکۆرد (Embed)
        embed = discord.Embed(
            title="🌐 زانیاری ناونیشانی IP",
            color=discord.Color.blue()
        )
        embed.add_field(name="IP", value=data.get("ip", "Unknown"), inline=False)
        embed.add_field(name="وڵات", value=data.get("country", "Unknown"), inline=True)
        embed.add_field(name="هەرێم/پارێزگا", value=data.get("region", "Unknown"), inline=True)
        embed.add_field(name="شار", value=data.get("city", "Unknown"), inline=True)
        embed.add_field(name="کۆمپانیای خزمەتگوزاری (ISP)", value=connection.get("isp", "Unknown"), inline=False)
        embed.add_field(name="کاتی ناوچە (Timezone)", value=timezone.get("id", "Unknown"), inline=True)

        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if latitude is not None and longitude is not None:
            map_link = f"https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}"
            embed.add_field(name="سەیرکردن لەسەر نەخشە", value=f"[کلیک لێرە بکە]({map_link})", inline=False)

        embed.set_footer(text="زانیارییەکان نزیکەیین و سەد لە سەد تەواو نیین.")
        
        await ctx.send(embed=embed)

    except (HTTPError, URLError, TimeoutError, OSError) as error:
        await ctx.send(f"❌ داواکاری تۆڕەکە سەرکەوتوو نەبوو: {error}")
    except (json.JSONDecodeError, ValueError):
        await ctx.send("❌ نەتوانرا وەڵامی خزمەتگوزارییەکە بخوێنرێتەوە.")

# لێرە تووکنەکەی بۆتەکەت دادەنێیت
bot.run("YOUR_DISCORD_BOT_TOKEN")
