import discord
import responses
import logger
import asyncio
from gtts import gTTS

from discord.ext import commands
from typing import Final
from yt_helper import youtube_url_validation, check_video_availability, get_video_name

async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as exception:
        logger.log(str(exception), logger.MessageType.error)

def run_discord_bot():
    TOKEN = "YOUR TOKEN ;)"

    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(intents = intents, command_prefix = "/")

    bot_activity_info = {
        "isSpeaking": False,
        "isPlayingMusic": False,
        "inVoiceChannel": False
    }

    music_queue = []

    DED_TAG: Final[str] = "6139"

    def is_music_playing() -> bool:
        return bot_activity_info["isPlayingMusic"]

    def is_speaking() -> bool:
        return bot_activity_info["isSpeaking"]

    def in_voice_channel() -> bool:
        return bot_activity_info["inVoiceChannel"]

    def set_music_playing(is_music_playing: bool):
        bot_activity_info["isPlayingMusic"] = is_music_playing

    def set_speaking(is_speaking: bool):
        bot_activity_info["isSpeaking"] = is_speaking
        
    def set_in_voice_channel(in_vc: bool):
        bot_activity_info["inVoiceChannel"] = in_vc

    # NOTE: ______Bot commands______
    # NOTE: Speaking Commands

    @client.command(name='interrupt_speaking')
    async def interrupt_speaking(ctx):
        global vc

        if ctx.author.discriminator != DED_TAG:
            return

        if is_speaking():
            vc.stop()
            set_speaking(False)
  
    @client.event
    async def on_message(message):
        global vc

        if message.author.discriminator != DED_TAG:
            return

        if message.content[0] == "/":
            await client.process_commands(message)
            return

        if is_music_playing():
            await message.channel.send('Погоди, музыка играет - не могу базарить')
            return

        if is_speaking():
            await message.channel.send('Деда, я еще базарю - погоди, пока закончу')
            return

        if not in_voice_channel():
            await message.channel.send('Деда, ну пропиши `/connect_voice` комманду, шизик ты старый')
            return

        output_audio = gTTS(text = str(message.content), lang = "ru", slow = False)
        output_audio.save("output.mp3")

        user = message.author
        voice = message.author.voice

        if voice != None:
            set_speaking(True)
            try:
                vc.play(
                    discord.FFmpegPCMAudio(
                        executable = "ffmpeg-master-latest-win64-gpl-shared\\bin\\ffmpeg.exe",
                        source = 'output.mp3'
                    )
                )
            except Exception as e:
                await message.channel.send(f'Произошел кринж - {e.args[0]}')

            while vc.is_playing():
                await asyncio.sleep(1)

            vc.stop()
            set_speaking(False)
        else:
            logger.log(f'{str(user)} is not in a channel.', logger.MessageType.warning)
            await message.channel.send(f'{str(user)} is not in a channel.')

    # NOTE: Music commands

    @client.command(name='add_to_queue')
    async def add_to_queue(ctx, url = None, pos = None):
        if url == None:
            await ctx.send("Ну ссылку засунь хоть для начала..")
            return

        if not youtube_url_validation(url):
            await ctx.send("Ссылка не валидная. Должна быть ссылка с ютуба.")
            return

        if not check_video_availability(url):
            await ctx.send("Видосик недоступен, произошел кринж")
            return

        int_pos = 0
        name = get_video_name(url)

        if not pos is None:
            try:
                int_pos = int(pos)
            except:
                await ctx.send("Вторым параметром надо целое число писать, циферку, понимаешь?")
                return

        if (not pos is None) and int_pos <= 0:
            await ctx.send("Позиция трека может начинаться с 1-й, гений (ну как ты в очереди будешь нулевым или минусовым, подумай)")
            return

        track = dict()
        track["name"] = name
        track["url"] = url

        if pos is None or int_pos - 1 >= len(music_queue):
            music_queue.append(track)
            await ctx.send(f"Вы добавили трек `{name}` в конец очереди")
        else:
            music_queue.insert(int_pos - 1, track)
            await ctx.send(f"Вы добавили трек `{name}` на `{pos}-ю` позицию")

    @client.command(name='remove_from_queue')
    async def remove_from_queue(ctx, *args):
        removed_count = 0

        indicies = []
        names = []

        for arg in args:
            if arg.isdigit():
                pos = int(arg) - 1
                indicies.append(pos)
            else:
                names.append(arg)

        indicies = sorted(indicies, key = int, reverse = True)

        for index in indicies:
            if index < len(music_queue):
                del(music_queue[index])
                removed_count += 1

        if removed_count == 0:
            await ctx.send("По вашему запросу не было найдено треков для удаления")
        elif removed_count == 1:
            await ctx.send("Удален 1 трек")
        else:
            await ctx.send(f"Удалено {removed_count} треков")

    @client.command(name='display_queue')
    async def display_queue(ctx):
        queue_str = "**Ваша очередь треков:**\n"
        index = 1
        for track in music_queue:
            track_name = track["name"]
            queue_str += f"{index}) `{track_name}`\n"
            index += 1
        await ctx.send(queue_str)

    # NOTE: Other commands

    @client.command(name='connect_voice')
    async def connect(ctx):
        global vc
        if ctx.author.discriminator != DED_TAG:
            return

        voice = ctx.author.voice

        if voice != None:
            voice_channel = voice.channel
            vc = await voice_channel.connect()
            set_in_voice_channel(True)
        else:
            logger.log(f'{str(ctx.author)} is not in a channel.', logger.MessageType.warning)
            await ctx.send(f'{str(ctx.author)} is not in a channel.')

    @client.command(name='disconnect_voice')
    async def disconnect(ctx):
        global vc

        if ctx.author.discriminator != DED_TAG:
            return

        voice = ctx.author.voice
            
        if voice != None:
            await vc.disconnect()
            set_in_voice_channel(False)
        else:
            logger.log(f'{str(ctx.author)} is not in a channel.', logger.MessageType.warning)
            await ctx.send(f'{str(ctx.author)} is not in a channel.')

    @client.command()
    async def ping(ctx):
        ping_ = client.latency
        ping =  round(ping_ * 1000)
        await ctx.send(f"{str(ctx.author)} ping is `{ping}ms`")

    @client.event
    async def on_ready():
        logger.log(f'{client.user} is now running! What masterpiece shall we play today?', logger.MessageType.info)

    @client.command()
    @commands.is_owner()
    async def shutdown(ctx):
        if ctx.author.discriminator != DED_TAG:
            print(ctx.author.discriminator)
            return
    
        await ctx.bot.close()

    client.run(TOKEN)