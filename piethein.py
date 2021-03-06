# piet Hein de Discord bot
# Gemaakt door: Nick Willems
# 05-01-22


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


token = ':)'
botpiet = commands.Bot(command_prefix = 'piet ')


# events
@botpiet.event
async def on_ready():

    await botpiet.change_presence(status=discord.Status.online, activity=discord.Game("De Zilvervloot"))
    print("Piet is online!")


# Music player
@botpiet.command(name='kom', help='piet joined the voice channel.')
async def speel(ctx):

    if not ctx.message.author.voice:
        await ctx.send("Je moet in een voice channel zitten om dit commando te gebruiken...")
        return

    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()

@botpiet.command(name='weg', help='Piet gaat uit de voice channel.')
async def weg(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

@botpiet.command(name='speel', help='Geef Piet een youtube link dan speelt hij deze voor je af.')
async def speel(ctx, url):
    voice_client = ctx.message.guild.voice_client

    if ctx.voice_client.is_playing():
        voice_client.pause()

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=botpiet.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        
        await ctx.send('**Vette compositie:** {}'.format(player.title))

    else:
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=botpiet.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        
        await ctx.send('**Vette compositie:** {}'.format(player.title))

@botpiet.command(name='stop', help='Piet stopt met spelen van muziek.')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    voice_client.pause()

@botpiet.command(name='volume', help='Verander het volume van piet met een cijfer')
async def volume(ctx, volume: int):

    ctx.voice_client.source.volume = volume / 100
    await ctx.send("Volume veranderd naar {}%".format(volume))


botpiet.run(token)
