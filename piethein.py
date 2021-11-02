# discord bot in python 
# 22 mei 2021
# Nick Willems


import discord
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
import youtube_dl
import asyncio


#youtube downloader (van de yt_dl website geplukt...)
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' 
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)




botpiet = commands.Bot(command_prefix = "piet ")


#random events
@botpiet.event
async def on_ready():
    await botpiet.change_presence(status=discord.Status.online, activity=discord.Game("West-Indische Compagnie"))
    print("Piet Hein is alive.")

@botpiet.event 
async def on_member_join(member):
    print(f"{member} has joined the server.")
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f"Welkom aanboord {member.mention}! Hopelijk wordt je niet snel zeeziek!")

@botpiet.event
async def on_member_remove(member):
    print (f"{member} is weggegaan :( ")




#random commands
@botpiet.command(name="hey", help="Piet zegt hallo terug." )
async def hey(ctx):
    await ctx.send("wsup my dude. Mijn naam is Pieter Pietersen Heyn.")

@botpiet.command(name="ping", help="Laat ping zien van Piet." )
async def ping(ctx):
    await ctx.send(f"latency is {round(botpiet.latency * 1000)}ms")




#music player commands
@botpiet.command(name='speel', help='Geef Piet een youtube link dan speelt hij deze voor je af.')
async def speel(ctx, url):
    if not ctx.message.author.voice:
        await ctx.send("Je moet in een voice channel zitten om dit commando te gebruiken...")
        return

    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=botpiet.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**Now playing:** {}'.format(player.title))


@botpiet.command(name='stop', help='Piet stopt met spelen van muziek.')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()




botpiet.run("PM9YGEKbGarSgl6zMxlrejpgUA2cR73i") 
