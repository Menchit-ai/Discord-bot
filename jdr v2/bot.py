# bot.py
import os
import shutil
import pathlib

import random
import json
from spellchecker import SpellChecker

import discord
from discord.ext import commands


TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
bot = commands.Bot(command_prefix='/')

######  CHEMIN DE BASE  #########
path_data     = "./data/"
path_sys_json = "./data/system.json"
path_sys_txt  = "./data/system.txt"
path_sound    = "./data/data_sound/"
#################################


async def play(ctx,path):
    try:
        voice_channel = ctx.author.voice
        if voice_channel is None: await ctx.send("Vous n'êtes pas dans un channel audio."); return
        vc = None


        if (ctx.me.voice is None): 
            vc = await ctx.author.voice.channel.connect()
        elif ctx.author.voice.channel != ctx.me.voice.channel:
            await ctx.voice_client.disconnect()
            vc = await ctx.author.voice.channel.connect()
        else:
            vc = ctx.voice_client    

        vc.play(discord.FFmpegPCMAudio(path))
        vc.is_playing()
    except:
        pass

def spellcheck(words):
    spell = SpellChecker(language=None)
    spell.word_frequency.load_words(words)
    return spell

def get_sys(ctx):
    pass

# toutes les commandes disponibles avec le bot
@bot.command(name='emb')
async def emb(ctx):
    embed=discord.Embed(title="Tile", description="Desc", color=0x00ff00)
    embed.add_field(name="Fiel1", value="hi", inline=False)
    embed.add_field(name="Field2", value="hi2", inline=True)
    await ctx.send(embed=embed)

@bot.command(name='system', aliases=['sys'], help='Permet de définir le système de jeu utilisé dans tout le serveur Discord. option : c (nouveau système)')
async def change_system(ctx, newstate:str, option:str=None):

    with open(path_sys_txt) as f:    sys = [i.strip() for i in f.readlines()]
    spell = spellcheck(sys)
    try : newstate = spell.correction(newstate)
    except : pass

    if option is "c":
        if newstate in sys:
            await ctx.send(newstate + " est déjà présent dans les systèmes utilisables !")
            return
        with open(path_sys_txt,'a') as filesys:
            w = newstate+'\n'
            filesys.write(w)
            await ctx.send(newstate + " a bien été ajouté aux systèmes jouables !")

    if option is "d":
        with open(path_sys_txt,'w') as filesys:
            try:
                sys.remove(newstate)
            except:
                await ctx.send(newstate + " ne fait pas partie de la liste.")
                return
            filesys.write("\n".join(sys))
            filesys.write('\n')
        
        data = {}
        with open(path_sys_json,'r') as json_file:
            try: data = json.load(json_file)
            except:pass
        todel = []
        for key,value in data.items():
            if value == newstate:
                todel.append(key)
        for key in todel:
            data.pop(key)
        with open(path_sys_json,'w') as json_file:
            json.dump(data,json_file)
        await ctx.send(newstate + " a bien été supprimé de la liste.")
        return
    if not (newstate in sys) : await ctx.send("Ce système n'est pas disponible pour le moment."); return
    data = {}
    with open(path_sys_json,'r') as json_file:
        try : data = json.load(json_file)
        except : data = {}
    with open(path_sys_json,'w') as json_file:
        guild = ctx.guild.name
        data[guild] = newstate
        json.dump(data,json_file)
        await ctx.send("le serveur " + guild + " utilise maintenant le système " + newstate + ".")
        
    return

@bot.command(name='info', aliases=['i'], help='Informations générales.')
async def show(ctx):
    await ctx.send(ctx.author)
    await ctx.send(ctx.guild)
    with open(path_sys_json,'r') as json_file:
        data = json.load(json_file)
        sys = 'None'
        try : sys = data[ctx.guild.name]
        except : pass
        await ctx.send(sys)
    await ctx.send("Tous les systèmes disponibles :")
    sys = None
    with open(path_sys_txt,'r') as f:
        sys = [i.strip() for i in f.readlines()]
    for i in sys:
        await ctx.send(i)



@bot.command(name='roll', aliases=['r'], help='Fait un test sous une compétence données en utilisant un personnage avec un modificateur optionnel.')
async def lilroll(ctx, character: str, test: str, mod: int=0):
    # bug boucle avec modificateur négatif
    spell = SpellChecker(language=None)
    character = character.lower()
    test = test.lower()
    roll = random.randint(1,100)
    if roll <= 10: await play(ctx,'./data/data_sound/victory.mp3')
    elif roll >= 90 : await play(ctx,'./data/data_sound/fail.mp3')
    else : await play(ctx,'./data/data_sound/dice_sound.mp3')
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
        result = result + "Roll : " + str(roll) + "/" + str(data[test]+mod) + ', '
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

@bot.command(name='carac', help='Liste toutes les caractéristiques disponibles pour le personnage.')
async def lilroll(ctx, character: str):
    if len(character) == 1 : character = trans[character]
    path = './data_characters/' + character + '.json'
    result = ''
    with open(path,'r') as json_file:
        data = json.load(json_file)
        result = "\n".join(data.keys())
    await ctx.send(result)

@bot.command(name='characters', help='Liste tous les personnages disponibles. (va disparaitre)')
async def listCharacter(ctx):
    path = os.getcwd() + '/data_characters'
    files = os.listdir(path)
    f = [f.split('.')[0] for f in files]
    result = "\n".join(f)
    await ctx.send(result)


@bot.command(name='shutdown', aliases=['sd','quit'], help='Termine le bot.')
async def shutdown(ctx):
    global vc
    try:
        await ctx.voice_client.disconnect()
    except:
        pass
    await client.close()
    await ctx.send("Shutdown")
    print("Bot closed")
    exit(0)

@bot.command(name='dice', aliases=['d'], help='Lance des dés [n°dés]d[n°faces]')
async def dice(ctx,dice:str):
    dice = dice.lower()
    dices, faces = map(int,dice.split('d'))

    li = []
    for i in range(dices):
        li.append(random.randint(1,faces))
    li = list(map(int,li))

    result = str(sum(li)) + '\n' + 'Details : ' + dice + " " + str(li)
    await ctx.send(result)


@bot.event
async def on_ready():
    print('Connected to Discord!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,name='/help'))

# gestion de toutes les erreurs
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error,commands.errors.ClientException):
        pass
    else:
        print(error)
        await ctx.send(error)

bot.run(TOKEN)