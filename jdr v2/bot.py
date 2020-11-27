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
path_sound    = "./data/data_sound/"
path_sys      = "./data/data_sys/"
path_sys_json = path_sys + "system.json"
path_sys_txt  = path_sys + "system.txt"
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
    guild = ctx.guild.name
    with open(path_sys_json,'r') as json_file:
        data = json.load(json_file)
        try : return data[guild]
        except : return None

# toutes les commandes disponibles avec le bot

@bot.command(name='createc', aliases=['cc'], help="Commande pour créer son personnage, alias : cc.")
async def create_character(ctx, name:str):
    sys = get_sys(ctx)
    user = ctx.author.name
    if sys is None : await ctx.send("Le serveur n'utilise actuellement aucun système, choisissez-en un !"); return

    path = path_sys + sys + '/' + user + '/'
    if not os.path.isdir(path) : os.mkdir(path)
    
    path = path + name + '.json'

    if os.path.isfile(path) : await ctx.send("Ce personnage existe déjà."); return
    
    with open(path, 'w') as json_file:
        json.dump({"test":1} , json_file)

    await ctx.send("Le personnage {} a bien été créé pour le joueur {}.".format(name,user))


@bot.command(name='add_carac', aliases=['ac'], help='Ajoute des capacités dans la liste des capacités disponibles du système courant, alias : ac.')
async def add_carac(ctx, *carac:str):
    sys = get_sys(ctx)
    if sys is None : await ctx.send("Choisissez le système courant auquel ajouter les caractéristiques"); return
    with open(path_sys + sys + '/' + sys + '.txt', 'a') as _file : _file.write("|".join(carac))
    await ctx.send("Les caractéristiques suivantes ont été ajoutés au système " + sys + " : " + ", ".join(carac) + '.')

@bot.command(name='rm_carac', aliases=['rc'], help='Supprime des capacités dans la liste des capacités disponibles du système courant, alias : rc.')
async def rm_carac(ctx, *carac:str):
    sys = get_sys(ctx)
    if sys is None : await ctx.send("Choisissez le système courant duquel supprimer les caractéristiques"); return
    data = []
    with open(path_sys + sys + '/' + sys + '.txt', 'r') as _file : data = _file.read().split('|')
    data = [x for x in data if x not in carac]
    with open(path_sys + sys + '/' + sys + '.txt', 'w') as _file : _file.write('|'.join(data))
    await ctx.send("Voici les nouvelles caractéristiques du système " + sys + " : " + ", ".join(data) + '.')

@bot.command(name='show_carac', aliases=['sc'], help='Montre les capacités disponibles du système courant, alias : sc.')
async def rm_carac(ctx):
    sys = get_sys(ctx)
    if sys is None : await ctx.send("Choisissez le système courant duquel supprimer les caractéristiques"); return
    data = []
    with open(path_sys + sys + '/' + sys + '.txt', 'r') as _file : data = _file.read().split('|')
    if data[0] == '' and len(data) == 1: await ctx.send("Il n'y a pas encore de caractéristiques dans ce système."); return
    await ctx.send("\n".join(data))


@bot.command(name='system', aliases=['sys'], help='Permet de définir le système de jeu utilisé dans tout le serveur Discord. option : c (nouveau système)')
async def change_system(ctx, newstate:str, option:str=None):

    with open(path_sys_txt) as f:    sys = [i.strip() for i in f.readlines()]
    
    if option is "c":
        if newstate in sys:
            await ctx.send(newstate + " est déjà présent dans les systèmes utilisables !")
            return
        with open(path_sys_txt,'a') as filesys:
            w = newstate+'\n'
            filesys.write(w)
            
        try:
            path = path_sys + newstate
            os.mkdir(path)
            path = path + '/' + newstate + '.txt'
            open(path,'a').close()
        except:
            await ctx.send("Le dossier n'a pas pu être créé.")

        await ctx.send(newstate + " a bien été ajouté aux systèmes jouables !")
        return

    spell = spellcheck(sys)
    try : newstate = spell.correction(newstate)
    except : pass

    if option is "d":
        with open(path_sys_txt,'w') as filesys:
            try:
                sys.remove(newstate)
            except:
                await ctx.send(newstate + " ne fait pas partie de la liste.")
                return
            for s in sys:
                w = s+'\n'
                filesys.write(w)
        
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

        try:
            path = path_sys + newstate
            shutil.rmtree(path)
        except:
            await ctx.send("Le dossier n'a pas pu être supprimé.")

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
    user = ctx.author.name
    guild = ctx.guild.name
    curr_sys = "None"
    with open(path_sys_json,'r') as json_file:
        data = json.load(json_file)
        try : curr_sys = data[ctx.guild.name]
        except : pass
    sys = "None"
    try:
        with open(path_sys_txt,'r') as f:
            sys = [i.strip() for i in f.readlines()]
        sys = ", ".join(sys)
    except:sys="None"
    embed = discord.Embed(title= "Infos générales")
    embed.add_field(name="user", value=user, inline=False)
    embed.add_field(name="guild", value=guild, inline=False)
    embed.add_field(name="current system", value=curr_sys, inline=False)
    if not (sys == ""): embed.add_field(name="available systems", value=sys, inline=False)
    await ctx.send(embed=embed)



@bot.command(name='roll', aliases=['r'], help='Fait un test sous une compétence données en utilisant un personnage avec un modificateur optionnel.')
async def lilroll(ctx, test: str, mod: int=0):

    roll = random.randint(1,100)
    if roll <= 10: await play(ctx,path_sound+'victory.mp3')
    elif roll >= 90 : await play(ctx,path_sound+'fail.mp3')
    else : await play(ctx,path_sound+'dice_sound.mp3')


    with open(path,'r') as json_file:
        data = json.load(json_file)
        keys = data.keys()
        spell.word_frequency.load_words(keys)
        test = test.lower()
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
    await bot.change_presence(status=discord.Status.offline)
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