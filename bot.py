import discord
import responses
import logger
import asyncio
from gtts import gTTS

from discord.ext import commands

async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as exception:
        logger.log(str(exception), logger.MessageType.error)

def run_discord_bot():
    TOKEN = "MTA0MTEyMDU5NzY3NTEwMjQxOQ.GCo-Ai.R05nlSVlzSftDgGdH112lBPbb_OC-7iOMpm6Jg"

    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(intents = intents, command_prefix = "/")

    DED_TAG = "6139"

    vc = None

    @client.command(name='connect_voice')
    async def connect(ctx):
        global vc
        if ctx.author.discriminator != DED_TAG:
            print(ctx.author.discriminator)
            return

        voice = ctx.author.voice

        if voice != None:
            voice_channel = voice.channel
            vc = await voice_channel.connect()
        else:
            logger.log(f'{str(ctx.author)} is not in a channel.', logger.MessageType.warning)
            await ctx.send(f'{str(ctx.author)} is not in a channel.')

    @client.command(name='disconnect_voice')
    async def disconnect(ctx):
        global vc

        if ctx.author.discriminator != DED_TAG:
            print(ctx.message.author.discriminator)
            return

        await vc.disconnect()

    @client.event
    async def on_ready():
        logger.log(f'{client.user} is now running!', logger.MessageType.info)

    @client.command()
    async def ping(ctx):
        ping_ = client.latency
        ping =  round(ping_ * 1000)
        await ctx.send(f"{str(ctx.author)} ping is {ping}ms")
  
    @client.event
    async def on_message(message):
        global vc

        if message.author.discriminator != DED_TAG:
            print(message.author.discriminator)
            return

        if message.content[0] == "/":
            await client.process_commands(message)
            return

        output_audio = gTTS(text = str(message.content), lang = "ru", slow = False)
        output_audio.save("output.mp3")

        user = message.author
        voice = message.author.voice

        if voice != None:
            vc.play(
                discord.FFmpegPCMAudio(
                    executable = "ffmpeg-master-latest-win64-gpl-shared\\bin\\ffmpeg.exe",
                    source = 'output.mp3'
                )
            )

            while vc.is_playing():
                await asyncio.sleep(1)

            vc.stop()
        else:
            logger.log(f'{str(user)} is not in a channel.', logger.MessageType.warning)
            await message.channel.send(f'{str(user)} is not in a channel.')

    @client.command()
    @commands.is_owner()
    async def shutdown(ctx):
        if ctx.author.discriminator != DED_TAG:
            print(ctx.author.discriminator)
            return
    
        await ctx.bot.close()

    client.run(TOKEN)