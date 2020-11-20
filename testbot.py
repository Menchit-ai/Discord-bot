# bot.py
import os
import random
import json
from spellchecker import SpellChecker
import pickle

import discord
from discord.ext import commands


TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
bot = commands.Bot(command_prefix='|')
trans = {'p':'pilote', 'a':'astrophysicien','i':'ingenieur','x':'xenobiologiste'}


async def play(ctx,path):

    voice_channel = ctx.author.voice
    if voice_channel is None: await ctx.send("Vous n'êtes pas dans un channel audio."); return
    voice_channel = voice_channel.channel

    try:
        vc = await voice_channel.connect()
        pickle.dump(vc, open('vc.VoiceChannel','wb'))
    except:
        vc = pickle.load(open('vc.VoiceChannel','rb'))

    vc.play(discord.FFmpegPCMAudio(path), after=lambda e: print('done', e))
    vc.is_playing()


# toutes les commandes disponibles avec le bot

@bot.command(name='roll', aliases=['r'], help='Make a test under a score for a specified character with an optionnal modifier.')
async def lilroll(ctx, character: str, test: str, mod: int=0):
    spell = SpellChecker(language=None)

    roll = random.randint(1,100)
    if roll <= 10: await play(ctx,'./data_sound/victory.mp3')
    elif roll >= 90 : await play(ctx,'./data_sound/fail.mp3')
    else : await play(ctx,'./data_sound/dice_sound.mp3')
    if len(character) == 1 : character = trans[character]
    path = './data_characters/' + character + '.json'
    result = character + ' rolling for '
    with open(path,'r') as json_file:
        data = json.load(json_file)
        keys = data.keys()
        spell.word_frequency.load_words(keys)
        test = spell.correction(test)
        result = result + test + ' \n'
        if not test in keys: await ctx.send("La caractéristique n'est pas reconnue."); return
        result = result + "Roll : " + str(roll) + "/" + str(data[test]-mod) + ', '
        if roll <= 10:
            result = result + "SUCCES CRITIQUE !!!"
        elif roll >= 90:
            result = result + "ECHEC CRITIQUE !!!"
        elif roll <= data[test] + mod:
            result = result + "reussite ! "
        elif roll > data[test] + mod:
            result = result + "echec ! "
        else:
            await ctx.send("check spelling")
            return
    await ctx.send(result)

@bot.command(name='carac', help='List all caracteristics available to a character.')
async def lilroll(ctx, character: str):
    if len(character) == 1 : character = trans[character]
    path = './data_characters/' + character + '.json'
    result = ''
    with open(path,'r') as json_file:
        data = json.load(json_file)
        result = "\n".join(data.keys())
    await ctx.send(result)

@bot.command(name='characters', help='List all characters available.')
async def listCharacter(ctx):
    path = os.getcwd() + '/data_characters'
    files = os.listdir(path)
    f = [f.split('.')[0] for f in files]
    result = "\n".join(f)
    await ctx.send(result)


@bot.command(name='shutdown', aliases=['sd','quit'], help='Kill the bot.')
async def shutdown(ctx):
    vc = None
    try:
        pickle.load(open('vc.VoiceChannel','rb'))
    except:
        pass
    await ctx.send("Shutdown.")
    try:
        await vc.disconnect()
    except:
        pass
    await client.close()
    print("Bot closed")
    exit(0)

@bot.event
async def on_ready():
    print('Connected to Discord!')

# gestion de toutes les erreurs
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error,commands.errors.ClientException):
        pass
    else:
        await ctx.send(error)

bot.run(TOKEN)