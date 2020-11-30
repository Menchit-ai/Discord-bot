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
        except : return "None"

def get_carac(ctx):
    sys = get_sys(ctx)
    data = []
    with open(path_sys + sys + '/' + sys + '.txt', 'r') as _file: data = _file.read().split('|')
    return data

def get_character(ctx):
    sys = get_sys(ctx)
    user = ctx.author.name
    path = path_sys + sys+'/' + 'character.json'
    data = {}
    try:
        with open(path,'r') as json_file : data = json.load(json_file)
    except : data = None
    c = "None"
    try : c = data[user]
    except : pass
    return c


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
    
    carac = get_carac(ctx)
    if carac[0] == '' : await ctx.send("Le système " + sys + " n'a pas de caractéristique propre."); return

    await ctx.send("Il faut maintenant renseigner les valeurs de chaque caractéristique")


    def check(author):
        def inner_check(message): 
            if message.author != author:
                return False
            try: 
                int(message.content) 
                return True 
            except ValueError:
                return False
        return inner_check

    stats = {}
    i = 0
    await ctx.send("Saisissez vos valeurs de caractéristiques, les nombres doivent être positifs et entiers.")
    while( i < len(carac) ):
        c = carac[i]
        await ctx.send(c + " : ")
        msg = await bot.wait_for('message', check=check(ctx.author),timeout=30)
        if not msg.author.name == user : continue
        try: 
            msg = int(msg.content)
            if not msg >= 0 : raise
            stats[c] = msg
            i = i + 1
        except:
            await ctx.send("Il y a eu un problème dans la lecture de votre saisie.")


    open(path,'w')
    with open(path, 'w') as json_file : json.dump(stats,json_file)

    show_stat = "Le personnage a les caractéristiques suivantes : "
    for key,value in stats.items():
        show_stat = show_stat + "\n" + key + " : " + str(value)

    await ctx.send("\nLe personnage {} a bien été créé pour le joueur {}.".format(name,user))
    await ctx.send(show_stat)

@bot.command(name='choose_character', aliases=['cch'], help="Permet à un joueur de choisir le personnage qu'il souhaite utiliser dans le système courant, alis : cch.")
async def funcname(ctx, character:str):
    sys = get_sys(ctx)
    path = path_sys + sys+'/' + 'character.json'
    data = {}
    with open(path,'r') as json_file : 
        try : data = json.load(json_file)
        except:pass
    user = ctx.author.name
    _path = path_sys + sys+'/' + user

    if not character in [f.split('.')[0] for f in os.listdir(_path)] : await ctx.send("Le personnage n'est pas disponible."); return

    data[user] = character
    with open(path,'w') as json_file : json.dump(data,json_file)
    await ctx.send("Le personnage de " + user + " est maintenant " + character + ".")


@bot.command(name='add_carac', aliases=['ac'], help='Ajoute des capacités dans la liste des capacités disponibles du système courant, alias : ac.')
async def add_carac(ctx, *carac:str):
    sys = get_sys(ctx)
    if sys is None : await ctx.send("Choisissez le système courant auquel ajouter les caractéristiques"); return
    with open(path_sys + sys + '/' + sys + '.txt', 'r') as _file : data = _file.read().split('|')
    for c in carac: data.append(c)
    data = [d for d in data if not d==""]
    with open(path_sys + sys + '/' + sys + '.txt', 'w') as _file : _file.write("|".join(data))
    await ctx.send("Les caractéristiques suivantes ont été ajoutés au système " + sys + " : " + ", ".join(carac) + '.')

@bot.command(name='rm_carac', aliases=['rc'], help='Supprime des capacités dans la liste des capacités disponibles du système courant, alias : rc.')
async def rm_carac(ctx, *carac:str):
    if not ctx.author.name == "Menchrof" : await ctx.send("Vous n'avez pas la permission de supprimer des systèmes."); return
    sys = get_sys(ctx)
    if sys is None : await ctx.send("Choisissez le système courant duquel supprimer les caractéristiques"); return
    data = []
    with open(path_sys + sys + '/' + sys + '.txt', 'r') as _file : data = _file.read().split('|')
    data = [x for x in data if x not in carac]
    data = [d for d in data if not d==""]
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
            
        path = path_sys + newstate
        try:
            os.mkdir(path)
            _path = path + '/' + newstate + '.txt'
            open(_path,'a').close()
        except:
            await ctx.send("Le dossier n'a pas pu être créé.")

        _path = path + '/' + 'character' + '.json'
        open(_path,'a').close()

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

    try:
        with open(path_sys_json,'r') as json_file:
            data = json.load(json_file)
            curr_sys = data[ctx.guild.name]
    except : pass

    sys = "None"
    try:
        with open(path_sys_txt,'r') as f:
            sys = [i.strip() for i in f.readlines()]
        sys = ", ".join(sys)
    except:sys="None"

    character = get_character(ctx)
    all_character = "None"

    try : 
        if not sys == "None":
            _path = path_sys + curr_sys+'/' + user
            li = [f.split('.')[0] for f in os.listdir(_path)]
            all_character = ", ".join(li)
    except : pass

    embed = discord.Embed(title= "Infos générales")
    embed.add_field(name="user", value=user, inline=False)
    embed.add_field(name="guild", value=guild, inline=False)
    embed.add_field(name="current system", value=curr_sys, inline=False)
    if not (sys == ""): embed.add_field(name="available systems", value=sys, inline=False)
    if not (character == ""): embed.add_field(name="current character", value=character, inline=False)
    if not (all_character == ""): embed.add_field(name="available character", value=all_character, inline=False)
    await ctx.send(embed=embed)



@bot.command(name='roll', aliases=['r'], help='Fait un test sous une compétence données en utilisant un personnage avec un modificateur optionnel.')
async def lilroll(ctx, test: str, mod: int=0):
    
    user = ctx.author.name
    char = get_character(ctx)
    if char == "None" : await ctx.send("Vous n'utilisez actuellement aucun personnage."); return
    sys = get_sys(ctx)
    if sys == "None" : await ctx.send("Vous n'utilisez actuellement aucun système de jeu."); return
    # test = " ".join(test)
    test = test.lower()
    carac = get_carac(ctx)
    spell = spellcheck(carac)
    test = spell.correction(test)
    print(test)

    if test not in carac : await ctx.send("Le test n'est pas reconnu."); return

    _path_character = path_sys + sys+'/' + 'character.json'
    character = ""
    with open(_path_character,'r') as json_file : character = json.load(json_file)[user]
    
    _path_carac = path_sys + sys+'/' + user+'/' + character + '.json'
    
    data = {}
    with open(_path_carac,'r') as json_file : data = json.load(json_file)

    roll = random.randint(1,100)
    if roll <= 10: await play(ctx,path_sound+'victory.mp3')
    elif roll >= 90 : await play(ctx,path_sound+'fail.mp3')
    else : await play(ctx,path_sound+'dice_sound.mp3')

    value = data[test]

    result = char + " fait un test sous son " + test + " :\n" + str(roll) + '/' + str(value+mod) + " : "

    true_value = value + mod
    
    if roll <= 10: result = result + "SUCCES CRITIQUE !"
    elif roll >= 90: result = result + "ECHEC CRITIQUE !"
    elif roll <= true_value: result = result + "succès."
    elif roll > true_value: result = result + "échec."
    else: result = result + "valeur non interprétée."

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