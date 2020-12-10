import os
import time
import re
import subprocess
import shutil
import pathlib
import sys

import nacl

import random
from datetime import datetime
import json
from spellchecker import SpellChecker

import discord
from discord.ext import commands

TOKEN = os.getenv('DISCORD_TOKEN_WIP')
ME = os.getenv('DISCORD_ID_ME')
PATH = "D:/perso/discordBot/jdr release/config.json"

client = discord.Client()
bot = commands.Bot(command_prefix='_')

def get_config():
    data = {}
    with open(PATH,'r') as json_file:
        try: data = json.load(json_file)
        except: return -1
    return data

def update(data):
    with open(PATH,'w') as json_file:
        try: json.dump(data,json_file,indent=2, separators=(', ',': '), sort_keys=True, ensure_ascii=True)
        except: return -1
    return 1

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
    except RuntimeError as e:
        await mpme(e)

def spellcheck(words):
    spell = SpellChecker(language=None)
    spell.word_frequency.load_words(words)
    return spell

def get_system(ctx):
    guild = get_guild(ctx)
    config = get_config()
    try : return config["curr_sys"][guild]
    except : return None

def get_all_sys(ctx):
    guild = get_guild(ctx)
    config = get_config()
    try : return list(config["sys"].keys())
    except : return None

def get_user(ctx):
    return ctx.author.name

def get_guild(ctx):
    return ctx.guild.name

def get_carac(ctx):
    config = get_config()
    sys = get_system(ctx)
    try : return config["sys"][sys]["carac_system"]
    except : return None

def get_character(ctx):
    config = get_config()
    sys = get_system(ctx)
    user = get_user(ctx)
    try : return config["sys"][sys]["characters"][user]["curr_character"]
    except : return None

def get_all_character(ctx):
    config = get_config()
    system = get_system(ctx)
    user = get_user(ctx)
    try : return list(config["sys"][system]["characters"][user]["characters"].keys())
    except : return None

async def rollTFTL(ctx,config,user,character,system,test):
    test = test.split('+')
    carac = config["sys"][system]["characters"][user]["characters"][character]
    await play(ctx,'./data_sound/victory.mp3')

    for i in test : 
        if i not in carac : await ctx.send("Test non reconnu."); return

    nbdice = int(carac[test[0]]) + int(carac[test[1]])
    result = [random.randint(1,6) for i in range(nbdice)]
    if 6 in result:
        result = [str(i) for i in result]
        await ctx.send("Lancés : " + " ".join(result) + "\n" + "Réussite !")
    else :
        result = [str(i) for i in result]
        await ctx.send("Lancés : " + " ".join(result) + "\n" + "Echec !")

async def mpme(message):
    me = await bot.fetch_user(int(ME))
    await me.send(message)

async def quitter(ctx):
    try:
        await ctx.voice_client.disconnect()
    except:
        pass
    await client.close()
    await bot.change_presence(status=discord.Status.offline)


# toutes les commandes disponibles avec le bot

@bot.command(name='createc', aliases=['cc'], help="Commande pour créer son personnage, alias : cc.")
async def create_character(ctx, *name:str):
    if len(name) > 1 : name = " ".join(name)
    system = get_system(ctx)
    user = get_user(ctx)
    if system is None : await ctx.send("Le serveur n'utilise actuellement aucun système, choisissez-en un !"); return

    config = get_config()
    
    characters = get_all_character(ctx)

    if characters is None : config["sys"][system]["characters"][user] = {"characters":{},"curr_character":None}
    elif name in characters : await ctx.send("Ce personnage existe déjà."); return
    
    carac = get_carac(ctx)
    if len(carac)==0 : await ctx.send("Le système " + system + " n'a pas de caractéristique propre."); return

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
        await msg.add_reaction('👍')
        if not msg.author.name == user : continue
        try: 
            msg = int(msg.content)
            if not msg >= 0 : raise
            stats[c] = msg
            i = i + 1
        except:
            await ctx.send("Il y a eu un problème dans la lecture de votre saisie.")

    config["sys"][system]["characters"][user]["characters"][name] = stats

    if not update(config) : await ctx.send("Il y a eu un problème dans l'enregistrement des caractéristiques."); return

    show_stat = "Le personnage a les caractéristiques suivantes : "
    for key,value in stats.items():
        show_stat = show_stat + "\n" + key + " : " + str(value)

    await ctx.send("\nLe personnage {} a bien été créé pour le joueur {}.".format(name,user))
    await ctx.send(show_stat)


@bot.command(name="set_caracteristic", aliases=['setc'], help="Modifie la valeur d'une caractéristique du personnage courant, l'ajoute si elle n'existe pas, alias : setc.")
async def set_caracteristic(ctx, carac:str, value:int):
    
    config = get_config()
    user = get_user(ctx)
    guild = get_guild(ctx)
    character = get_character(ctx)
    if character is None : await ctx.send("Il faut choisir un personnage courant."); return
    system = get_system(ctx)
    if system is None : await ctx.send("Il faut choisir un système courant."); return
    
    caracteristics = config["sys"][system]["characters"][user]["characters"][character]
    caracteristics[carac] = value
    config["sys"][system]["characters"][user]["characters"][character] = caracteristics

    update(config)
    await ctx.send("Le personnage " + character + " a maintenant " + str(value) + " en carac.")
    
@bot.command(name='choose_character', aliases=['cch'], help="Permet à un joueur de choisir le personnage qu'il souhaite utiliser dans le système courant, alias : cch.")
async def choose_character(ctx, *character:str):
    if len(character) > 1 : character = " ".join(character)
    system = get_system(ctx)
    if system is None : await ctx.send("Choisissez un système."); return
    config = get_config()
    user = get_user(ctx)
    
    characters = get_all_character(ctx)

    if not character in characters : await ctx.send(character + " n'est pas disponible."); return

    config["sys"][system]["characters"][user]["curr_character"] = character

    if not update(config) : await ctx.send("Il y a eu un problème dans l'enregistrement."); return
    await ctx.send("Le personnage de " + user + " est maintenant " + character + ".")

@bot.command(name='show_character', aliases=['sch'], help="Permet à un joueur d'afficher son personnage actuel', alias : cch.")
async def funcname(ctx):
    system = get_system(ctx)
    if system is None : await ctx.send("Choisissez un système."); return
    config = get_config()
    user = get_user(ctx)
    character = get_character(ctx)
    if character is None : await ctx.send("Choisissez un personnage."); return

    caracteristics = config["sys"][system]["characters"][user]["characters"][character]

    embed = discord.Embed(title= character)
    
    for key,value in caracteristics.items():
        embed.add_field(name = key, value = str(value))
    await ctx.send(embed=embed)

@bot.command(name='add_carac', aliases=['ac'], help='Ajoute des capacités dans la liste des capacités disponibles du système courant, alias : ac.')
async def add_carac(ctx, *carac:str):
    sys = get_system(ctx)
    config = get_config()
    if sys is None : await ctx.send("Choisissez le système courant auquel ajouter les caractéristiques"); return

    caracteristics = config["sys"][sys]["carac_system"]
    for c in carac: caracteristics.append(c.lower())
    config["sys"][sys]["carac_system"] = caracteristics

    if not update(config) : await ctx.send("Il y a eu un problème dans l'enregistrement."); return
    await ctx.send("Les caractéristiques suivantes sont présentes dans " + sys + " : \n" + ", ".join(caracteristics) + '.')

@bot.command(name='rm_carac', aliases=['rc'], help='Supprime des capacités dans la liste des capacités disponibles du système courant, alias : rc.')
async def rm_carac(ctx, *carac:str):
    if not ctx.author.name == "Menchrof" : await ctx.send("Vous n'avez pas la permission de supprimer des systèmes."); return
    sys = get_system(ctx)
    config = get_config()
    if sys is None : await ctx.send("Choisissez le système courant duquel supprimer les caractéristiques"); return
    
    caracteristics = config["sys"][sys]["carac_system"]
    caracteristics = [x for x in caracteristics if x not in carac]
    caracteristics = [d for d in caracteristics if not d==""]
    config["sys"][sys]["carac_system"] = caracteristics

    if not update(config) : await ctx.send("Il y a eu un problème dans l'enregistrement."); return
    await ctx.send("Voici les nouvelles caractéristiques du système " + sys + " : " + ", ".join(caracteristics) + '.')

@bot.command(name='show_carac', aliases=['sc'], help='Montre les capacités disponibles du système courant, alias : sc.')
async def show_carac(ctx):
    system = get_system(ctx)
    config = get_config()
    if system is None : await ctx.send("Choisissez le système courant duquel supprimer les caractéristiques"); return
    
    caracteristics = config["sys"][system]["carac_system"]
    if len(caracteristics) == 0 : await ctx.send("Il n'y a pas encore de caractéristiques dans ce système."); return
    await ctx.send("Le système " + system + " possède les caractéristiques suivantes : " + ", ".join(caracteristics))

@bot.command(name="h", help="Affiche les aides des commandes")
async def h(ctx, option:str="g"):
    text = {}
    with open("./help.json",'r') as json_file : text = json.load(json_file)
    embed = discord.Embed(title= "Aide sur les commandes")

    for key,value in text["main"].items():
        embed.add_field(name=key, value=value, inline=False)

    msg = await ctx.send(embed=embed)

    await msg.add_reaction('1️⃣')
    await msg.add_reaction('2️⃣')
    await msg.add_reaction('3️⃣')

@bot.command(name='system', aliases=['sys'], help='Permet de définir le système de jeu utilisé dans tout le serveur Discord. option : c (nouveau système)')
async def change_system(ctx, newstate:str, option:str=None):

    config = get_config()
    systems = config["sys"].keys()
    user = get_user(ctx)
    guild = get_guild(ctx)
    
    if option == "c":
        if newstate in systems: await ctx.send(newstate + " est déjà présent dans les systèmes utilisables !");return
        
        config["sys"][newstate] = {"carac_system":[], "characters":{}}
        config["curr_sys"][guild] = newstate
        update(config)
        await ctx.send(newstate + " a bien été ajouté aux systèmes jouables et est maintenant le système courant.")
        return

    spell = spellcheck(systems)
    try : newstate = spell.correction(newstate)
    except : pass

    if option == "d":
        if not ctx.author.name == "Menchrof" : await ctx.send("Vous n'avez pas la permission d'effectuer cette commande."); return
        if newstate not in systems : await ctx.send(newstate + " ne fait pas partie de la liste."); return
        
        del config["sys"][newstate]

        for key,value in config["curr_sys"].items():
            if value == newstate : config["curr_sys"][key] = None

        update(config)

        await ctx.send(newstate + " a bien été supprimé de la liste.")
        return

    if not (newstate in systems) : await ctx.send("Ce système n'est pas disponible pour le moment."); return
    config["curr_sys"][guild] = newstate
    update(config)
    await ctx.send("le serveur " + guild + " utilise maintenant le système " + newstate + ".")
    
    return

@bot.command(name='info', aliases=['i'], help='Informations générales.')
async def show(ctx):

    user = get_user(ctx)

    guild = get_guild(ctx)

    curr_sys = get_system(ctx)
    if curr_sys is None : curr_sys = "None"

    character = get_character(ctx)
    if character is None: character = "None"

    try : all_sys = ", ".join(list(get_all_sys(ctx)))
    except : all_sys = "None"
    if len(all_sys) == 0 : all_sys = "None"

    try : all_character = ", ".join(list(get_all_character(ctx)))
    except : all_character = "None"
    if len(all_character) == 0 : all_character = "None"

    embed = discord.Embed(title= "Infos générales")
    embed.add_field(name="user", value=user, inline=False)
    embed.add_field(name="guild", value=guild, inline=False)
    embed.add_field(name="current system", value=curr_sys, inline=False)
    embed.add_field(name="available systems", value=all_sys, inline=False)
    embed.add_field(name="current character", value=character, inline=False)
    embed.add_field(name="available character", value=all_character, inline=False)
    await ctx.send(embed=embed)



@bot.command(name='roll', aliases=['r'], help='Fait un test sous une compétence données en utilisant un personnage avec un modificateur optionnel.')
async def lilroll(ctx, test: str, mod: int=0):
    
    config = get_config()
    user = get_user(ctx)
    character = get_character(ctx)
    system = get_system(ctx)

    if character is None : await ctx.send("Vous n'utilisez actuellement aucun personnage."); return
    if system is None : await ctx.send("Vous n'utilisez actuellement aucun système de jeu."); return

    test = test.lower()

    if system == "TFTL" : await rollTFTL(ctx,config,user,character,system,test); return

    carac = config["sys"][system]["characters"][user]["characters"][character]  
    spell = spellcheck(carac)
    test = spell.correction(test)

    if test not in carac : await ctx.send("Le test n'est pas reconnu."); return

    roll = random.randint(1,100)
    if roll <= 10: await play(ctx,'./data_sound/victory.mp3')
    elif roll >= 90 : await play(ctx,'./data_sound/fail.mp3')
    else : await play(ctx,'./data_sound/dice_sound.mp3')

    value = carac[test]

    result = character + " fait un test sous son " + test + " :\n" + str(roll) + '/' + str(value+mod) + " : "

    true_value = value + mod
    
    if roll <= 10: result = result + "SUCCES CRITIQUE !"
    elif roll >= 90: result = result + "ECHEC CRITIQUE !"
    elif roll <= true_value: result = result + "succès."
    elif roll > true_value: result = result + "échec."
    else: result = result + "valeur non interprétée."

    await ctx.send(result)

@bot.command(name='carac', help='Liste toutes les caractéristiques disponibles pour le personnage.')
async def lilroll(ctx):
    config = get_config()
    system = get_system(ctx)
    user = get_user(ctx)
    character = get_character(ctx)
    if character is None: await ctx.send("Choisissez un personnage courant."); return
    caracteristics = list(config["sys"][system]["characters"][user]["characters"][character].keys())
    
    result = ", ".join(caracteristics)
    await ctx.send(result)


@bot.command(name='shutdown', aliases=['sd','quit'], help='Termine le bot.')
async def shutdown(ctx):
    if not ctx.author.name == "Menchrof" : await ctx.send("Vous n'avez pas la permission d'effectuer cette commande."); return
    await quitter(ctx)
    sys.exit(1)

@bot.command(name='update', help='Met le bot à jour.')
async def update_bot(ctx):
    if not ctx.author.name == "Menchrof" : await ctx.send("Vous n'avez pas la permission d'effectuer cette commande."); return

    shutil.copy("./config.json","./backup/backup_config.json")

    subprocess.Popen("main.exe", shell=True)
    await ctx.send("Redémarrage.")
    await quitter(ctx)
    sys.exit()


@bot.command(name='up', help='test')
async def shutdown(ctx):
    await ctx.send("Je suis up.")
    try:
        client.get_user(540934375810793473)
        client.get_user(234016737048264704)
    except Error as e : await mpme(str(e))

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

@bot.command(name="report", help="Use for report bug or way of improvements.")
async def report(ctx, *message:str):
    date = datetime.now()
    message = " ".join(message)
    message = str(date) + " : " + message
    await mpme(ctx.author.name + " : " + message)
    message = message  + "\n"
    message = message.encode("UTF-8")
    with open("D:/perso/discordBot/jdr release/report.txt",'ab') as f: f.write(message)
    await ctx.send("Votre rapport a bien été enregistré, merci.")

@bot.command(name="disconnect", help="disconnect from voice channel")
async def disconnect(ctx):
    try:
        await ctx.voice_client.disconnect()
    except:
        pass

@bot.event
async def on_ready():
    time.sleep(1)
    print('Connected to Discord!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,name='/h for help'))

@bot.event
async def on_reaction_add(reaction,user):
    if reaction.emoji == '1️⃣' and not user.id == 778899886087077909:
        text = {}
        with open("./help.json",'r') as json_file : text = json.load(json_file)

        embed = discord.Embed(title= "Comment créer son personnage ?")
        for key,value in text["create_character"].items():
            embed.add_field(name=key, value=value, inline=False)

        await reaction.message.edit(embed=embed)

    elif reaction.emoji == '2️⃣' and not user.id == 778899886087077909:
        text = {}
        with open("./help.json",'r') as json_file : text = json.load(json_file)

        embed = discord.Embed(title= "Comment créer son propre système ?")
        for key,value in text["create_system"].items():
            embed.add_field(name=key, value=value, inline=False)
        await reaction.message.edit(embed=embed)
    elif reaction.emoji == '3️⃣' and not user.id == 778899886087077909:
        text = {}
        with open("./help.json",'r') as json_file : text = json.load(json_file)

        embed = discord.Embed(title= "Informations générales")
        for key,value in text["miscelanous"].items():
            embed.add_field(name=key, value=value, inline=False)
        await reaction.message.edit(embed=embed)

# gestion de toutes les erreurs
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error,commands.errors.ClientException):
        await ctx.send(error)
    else:
        print(error)
        await ctx.send(error)


bot.run(TOKEN)