import os
import time
import re
import subprocess
import shutil
import pathlib
import sys

import random
from datetime import datetime
import json
from spellchecker import SpellChecker

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

TOKEN = os.getenv('DISCORD_TOKEN')
ME = os.getenv('DISCORD_ID_ME')
PATH = "D:/perso/discordBot/jdr release/config.json"
REACTIONS_DOC = ['0️⃣','1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']

client = discord.Client()

bot = commands.Bot(command_prefix='/')
bot.remove_command("help")

def get_config():
    # renvoie le dictionnaire contenu dans config.json
    data = {}
    with open(PATH,'r',encoding='utf-8') as json_file:
        try: data = json.load(json_file)
        except: return -1
    return data

def update(data):
    # enregistre le dictionnaire data dans le fichier config.json
    with open(PATH,'w',encoding='utf-8') as json_file:
        try: json.dump(data,json_file,indent=2, separators=(', ',': '), sort_keys=True, ensure_ascii=True)
        except: return -1
    return 1

async def play(ctx,path):
    # joue le fichier mp3 passé dans le path
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
        while vc.is_playing() : time.sleep(0.1)
        vc.disconnect()
    except Exception as e:
        await mpme(str(e))

async def jingle(id, voice_channel):
    try:
        vc = await voice_channel.connect()
        if   id ==  171623518772002816 : vc.play(discord.FFmpegPCMAudio("./data_sound/tu-tu-ru.mp3"))         # panda
        elif id ==  153158340799627265 : vc.play(discord.FFmpegPCMAudio("./data_sound/snk.mp3"))              # squiich
        elif id ==  311977846757392384 : vc.play(discord.FFmpegPCMAudio("./data_sound/chicken.mp3"))          # chicky
        elif id ==  226369729093304320 : vc.play(discord.FFmpegPCMAudio("./data_sound/10_MILLIONS.mp3"))      # sasuke
        elif id ==  224231591763902464 : vc.play(discord.FFmpegPCMAudio("./data_sound/pour-la-horde.mp3"))    # chevalier
        elif id ==  234391398441287680 : vc.play(discord.FFmpegPCMAudio("./data_sound/poubelle.mp3"))         # constantin
        elif id ==  466669390008549390 : vc.play(discord.FFmpegPCMAudio("./data_sound/nyctalope.mp3"))        # théo
        elif id ==  292348214047408129 : vc.play(discord.FFmpegPCMAudio("./data_sound/ludicolo.mp3"))         # ludicolo
        elif id ==  512022174853365770 : vc.play(discord.FFmpegPCMAudio("./data_sound/chipeur.mp3"))          # chippeur
        elif id ==  540919479832674334 : vc.play(discord.FFmpegPCMAudio("./data_sound/bresil.mp3"))           # major
        elif id ==  208294174909399040 : vc.play(discord.FFmpegPCMAudio("./data_sound/swain.mp3"))            # pierre
        elif id ==  540934375810793473 : vc.play(discord.FFmpegPCMAudio("./data_sound/kiwi.mp3"))             # thibaud
        elif id ==  290212793678954497 : vc.play(discord.FFmpegPCMAudio("./data_sound/pardon.mp3"))           # maillou
        elif id ==  126345523358597120 : vc.play(discord.FFmpegPCMAudio("./data_sound/baby-yoda.mp3"))        # romain
        elif id ==  250295841791672321 : vc.play(discord.FFmpegPCMAudio("./data_sound/yare-yare-daze.mp3"))   # nico
        elif id ==  234016737048264704 : vc.play(discord.FFmpegPCMAudio("./data_sound/ouii.mp3"))             # menchrof
        else : vc.play(discord.FFmpegPCMAudio("./data_sound/coucou.mp3")) # défaut
        while vc.is_playing():time.sleep(0.1)
        await vc.disconnect()
    except Exception as e:
        # await mpme(str(e))
        pass

def spellcheck(words):
    # initialise un objet spellcheck avec la liste de mot words dans le dictionnaire
    spell = SpellChecker(language=None)
    spell.word_frequency.load_words(words)
    return spell

def get_system(ctx):
    # renvoie le système courant du serveur
    guild = get_guild(ctx)
    config = get_config()
    try : return config["curr_sys"][guild]
    except : return None

def get_all_sys(ctx):
    # renvoie la liste de tous les systèmes utilisables
    guild = get_guild(ctx)
    config = get_config()
    try : return list(config["sys"].keys())
    except : return None

def get_user(ctx):
    # renvoie le nom de l'utilisateur ayant écrit le message
    return ctx.author.name

def get_guild(ctx):
    # renvoie la guild (serveur) du contexte
    return ctx.guild.name

def get_carac(ctx):
    # renvoie la liste des toutes les caractéristiques du système courant
    config = get_config()
    sys = get_system(ctx)
    try : return config["sys"][sys]["carac_system"]
    except : return None

def get_character(ctx):
    # renvoie le personnage courant de l'utilisateur
    config = get_config()
    sys = get_system(ctx)
    user = get_user(ctx)
    try : return config["sys"][sys]["characters"][user]["curr_character"]
    except : return None

def get_all_character(ctx):
    # renvoie tous les personnages du système courant et de l'utilisateur courant
    config = get_config()
    system = get_system(ctx)
    user = get_user(ctx)
    try : return list(config["sys"][system]["characters"][user]["characters"].keys())
    except : return None

def get_consummabels(ctx):
    # renvoie la liste de tous les consommables disponibles pour le personnages courant
    config = get_config()
    system = get_system(ctx)
    user = get_user(ctx)
    character = get_character(ctx)
    try : return list(config["sys"][system]["characters"][user]["characters"][character]["consommables"].keys())
    except : return None

def get_voice_channel(ctx):
    return ctx.voice_client

async def rollTFTL(ctx,config,user,character,system,test):
    # fait un jet de dés en utilisant une compétence
    # utilise un système où on lance xd6 (où x est la somme de deux compétences) et si on obtient au moins un 6 le jet est réussi
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

async def defaultRoll(ctx,config,user,character,system,test,mod):
    # fait un jet de dés en utilisant une compétence et en tenant compte d'un éventuel malus/bonus
    # utilise le système d100 : les caractéristiques vont de 1 à 100 et il faut faire inférieur ou égal à sa caractéristiques avec 1d100
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

async def mpme(message):
    # m'envoie un message privé via le bot
    me = await bot.fetch_user(int(ME))
    await me.send(message)

async def quitter(ctx):
    # permet d'arrêter le processus courant
    try:
        await ctx.voice_client.disconnect()
    except:
        pass
    await ctx.message.add_reaction('👍')
    await client.close()
    await bot.change_presence(status=discord.Status.offline)


# toutes les commandes disponibles avec le bot

@bot.command(name='createc', aliases=['cc'], help="Commande pour créer son personnage, alias : cc.")
async def create_character(ctx, *name:str):
    # permet la création de personnage
    if len(name) > 1 : name = " ".join(name)
    else : name = name[0]

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

    # cette fonction permet de ne prendre en compte que les messages de la personne créant son personnage
    # et de vérifier que les données entrées sont bien des entiers
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

    # le bot va capter tous les messages de l'utilisateur créant son personnage pour les associer aux caractéristiques demandées
    stats = {}
    stats["consommables"] = {}
    stats["inventaire"] = {}
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
        if key=="inventaire" or key=="consommables" : continue
        show_stat = show_stat + "\n" + key + " : " + str(value)
    # finalement on enregistre les valeurs dans le fichier de config et on affiche que tout s'est bien passé
    await ctx.send("\nLe personnage {} a bien été créé pour le joueur {}.".format(name,user))
    await ctx.send(show_stat)
    await ctx.send("Si vous voulez vous ajouter des ressources consommables (points de vie, munitions) utilisez la commande /uc et pour ajouter des objets à votre inventaire utiliser la commande /prendre.")

@bot.command(name='deletec', aliases=['dc'], help="Commande pour supprimer un de ses personnages, alias : dc.")
async def delete_character(ctx, *name:str):
    if len(name) > 1 : name = " ".join(name)
    else : name = name[0]
    config = get_config()
    user = get_user(ctx)
    guild = get_guild(ctx)
    system = get_system(ctx)
    if system is None : await ctx.send("Il faut choisir un système courant."); return
    characters = get_all_character(ctx)
    if not (name in characters) : await ctx.send("Le personnage n'existe pas."); return
    del config["sys"][system]["characters"][user]["characters"][name]

    if get_character(ctx) == name : config["sys"][system]["characters"][user]["curr_character"] = None

    update(config)
    await ctx.send("Le personnage {} a bien été supprimé.".format(name))



@bot.command(name="set_caracteristic", aliases=['setc'], help="Modifie la valeur d'une caractéristique du personnage courant, l'ajoute si elle n'existe pas, alias : setc.")
async def set_caracteristic(ctx, carac:str, value:int):
    # permet de modifier la valeur d'une caractéristique ou d'en créer une avec la valeur passée en paramètre
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

@bot.command(name="up_consumable", aliases=['uc'], help="Permet de modifier la valeur d'une ressource dîtes consommable, alise : uc")
async def up_consumable(ctx, consumable, value):
    system = get_system(ctx)
    user = get_user(ctx)
    if system is None : await ctx.send("Choisissez un système."); return
    character = get_character(ctx)
    if character is None : await ctx.send("Vous n'utilisez actuellement aucun personnage."); return
    config = get_config()
    if not consumable in get_consummabels(ctx) : config["sys"][system]["characters"][user]["characters"][character]["consommables"][consumable] = 0
    consume = float(config["sys"][system]["characters"][user]["characters"][character]["consommables"][consumable])
    value = float(value.replace(",","."))
    result = consume + value

    config["sys"][system]["characters"][user]["characters"][character]["consommables"][consumable] = result
    update(config)
    await ctx.send("Le personnage {} a maintenant {} {}".format(character,result,consumable))
    
@bot.command(name="prendre", aliases=['ramasser','take'], help="Permet d'ajouter un objet à son inventaire.")
async def prendre(ctx, objet, *description):
    system = get_system(ctx)
    user = get_user(ctx)
    character = get_character(ctx)
    if system is None : await ctx.send("Choisissez un système."); return
    if character is None : await ctx.send("Vous n'utilisez actuellement aucun personnage."); return
    config = get_config()
    inventaire = config["sys"][system]["characters"][user]["characters"][character]["inventaire"]
    if objet in inventaire.keys() : await ctx.send("Vous avez déjà cet objet dans votre ivnentaire."); return

    if len(description) == 0 : description = None
    elif len(description) == 1 : description = description[0]
    else : description = " ".join(description)

    inventaire[objet] = description
    config["sys"][system]["characters"][user]["characters"][character]["inventaire"] = inventaire
    update(config)
    await ctx.send("Vous avez pris l'objet {}.".format(objet))

@bot.command(name="lacher", aliases=['drop','utiliser'], help="Permet de supprimer un objet de son inventaire.")
async def lacher(ctx, objet):
    system = get_system(ctx)
    user = get_user(ctx)
    character = get_character(ctx)
    if system is None : await ctx.send("Choisissez un système."); return
    if character is None : await ctx.send("Vous n'utilisez actuellement aucun personnage."); return
    config = get_config()
    inventaire = config["sys"][system]["characters"][user]["characters"][character]["inventaire"]
    if not objet in inventaire.keys() : await ctx.send("Vous n'avez pas cet objet dans votre inventaire."); return
    del inventaire[objet]
    config["sys"][system]["characters"][user]["characters"][character]["inventaire"] = inventaire
    update(config)
    await ctx.send("Vous avez lâché l'objet {}.".format(objet))
    
@bot.command(name='choose_character', aliases=['cch'], help="Permet à un joueur de choisir le personnage qu'il souhaite utiliser dans le système courant, alias : cch.")
async def choose_character(ctx, *character:str):
    # définit le personnage passé en paramètre en tant que personnage courant
    if len(character) > 1 : character = " ".join(character)
    else : character = character[0]
    system = get_system(ctx)
    if system is None : await ctx.send("Choisissez un système."); return
    config = get_config()
    user = get_user(ctx)
    print(character)
    characters = get_all_character(ctx)
    if characters is None : await ctx.send("Vous n'avez pas de personnage dans ce système."); return
    if character is None : await ctx.send("Choisissez un personnage parmi " + ", ".join(characters))
    if not character in characters : await ctx.send(character + " n'est pas disponible."); return

    config["sys"][system]["characters"][user]["curr_character"] = character

    if not update(config) : await ctx.send("Il y a eu un problème dans l'enregistrement."); return
    await ctx.send("Le personnage de " + user + " est maintenant " + character + ".")

@bot.command(name='show_character', aliases=['sch'], help="Permet à un joueur d'afficher son personnage actuel', alias : sch.")
async def show_character(ctx):
    # affiche les caractéristiques du personnage courant
    system = get_system(ctx)
    if system is None : await ctx.send("Choisissez un système."); return
    config = get_config()
    user = get_user(ctx)
    character = get_character(ctx)
    if character is None : await ctx.send("Choisissez un personnage."); return

    caracteristics = config["sys"][system]["characters"][user]["characters"][character]

    embed = discord.Embed(title= character)
    
    for key,value in caracteristics.items():
        if key == "consommables" or key == "inventaire": continue
        embed.add_field(name = key, value = str(value))

    try:
        for key,value in caracteristics["consommables"].items():
            embed.add_field(name = key, value = str(value))
    except : pass

    inventaire = config["sys"][system]["characters"][user]["characters"][character]["inventaire"]
    if len(inventaire) > 0:
        for key,value in inventaire.items():
            embed.add_field(name = key, value= value)

    await ctx.send(embed=embed)

@bot.command(name='add_carac', aliases=['ac'], help='Ajoute des capacités dans la liste des capacités disponibles du système courant, alias : ac.')
async def add_carac(ctx, *carac:str):
    # ajoute la liste de caractéristiques au système courant
    sys = get_system(ctx)
    config = get_config()
    if sys is None : await ctx.send("Choisissez le système courant auquel ajouter les caractéristiques"); return

    caracteristics = config["sys"][sys]["carac_system"]

    for c in carac:
        c = c.replace("é","e")
        c = c.replace("è","e")
        c = c.replace("à","a")
        caracteristics.append(c.lower())
    caracteristics = sorted(caracteristics)

    config["sys"][sys]["carac_system"] = caracteristics

    if not update(config) : await ctx.send("Il y a eu un problème dans l'enregistrement."); return
    await ctx.send("Les caractéristiques suivantes sont présentes dans " + sys + " : \n" + ", ".join(caracteristics) + '.')

@bot.command(name='rm_carac', aliases=['rc'], help='Supprime des capacités dans la liste des capacités disponibles du système courant, alias : rc.')
async def rm_carac(ctx, *carac:str):
    # supprime la liste de caractéristiques du système courant, appel protégé
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
    # affiche les caractéristiques du système courant
    system = get_system(ctx)
    config = get_config()
    if system is None : await ctx.send("Choisissez le système courant duquel supprimer les caractéristiques"); return
    
    caracteristics = config["sys"][system]["carac_system"]
    if len(caracteristics) == 0 : await ctx.send("Il n'y a pas encore de caractéristiques dans ce système."); return
    await ctx.send("Le système " + system + " possède les caractéristiques suivantes : " + ", ".join(caracteristics))

@bot.command(name="help", aliases=['h'], help="Affiche les aides des commandes")
async def help(ctx, option:str="g"):
    # commande donnant accès à la doc de tout le bot
    text = {}
    with open("./help.json",'r',encoding='utf-8') as json_file : text = json.load(json_file)
    embed = discord.Embed(title= "Aide sur les commandes")

    for key,value in text[list(text.keys())[0]].items():
        embed.add_field(name=key, value=value, inline=False)

    msg = await ctx.send(embed=embed)

    for i in range(len(text.keys())):
        await msg.add_reaction(REACTIONS_DOC[i])

@bot.command(name='system', aliases=['sys'], help='Permet de définir le système de jeu utilisé dans tout le serveur Discord. option : c (nouveau système)')
async def change_system(ctx, newstate:str, option:str=None):
    # cette fonction permet la gestion de tous les systèmes, l'option c permet de créer un système, d permet de le supprimer
    config = get_config()
    systems = config["sys"].keys()
    user = get_user(ctx)
    guild = get_guild(ctx)
    
    if option == "c": #création d'un système
        if newstate in systems: await ctx.send(newstate + " est déjà présent dans les systèmes utilisables !");return
        
        config["sys"][newstate] = {"carac_system":[], "characters":{}}
        config["curr_sys"][guild] = newstate
        update(config)
        await ctx.send(newstate + " a bien été ajouté aux systèmes jouables et est maintenant le système courant.")
        return

    spell = spellcheck(systems)
    try : newstate = spell.correction(newstate)
    except : pass

    if option == "d": #suppression d'un système
        if not ctx.author.name == "Menchrof" : await ctx.send("Vous n'avez pas la permission d'effectuer cette commande."); return
        if newstate not in systems : await ctx.send(newstate + " ne fait pas partie de la liste."); return
        
        del config["sys"][newstate]

        for key,value in config["curr_sys"].items():
            if value == newstate : config["curr_sys"][key] = None

        update(config)

        await ctx.send(newstate + " a bien été supprimé de la liste.")
        return

    # si on ne supprime pas et qu'on ne crée pas on définie le système passé en paramètre en tant que système courant
    if not (newstate in systems) : await ctx.send("Ce système n'est pas disponible pour le moment."); return
    config["curr_sys"][guild] = newstate
    update(config)
    await ctx.send("le serveur " + guild + " utilise maintenant le système " + newstate + ".")
    
    return

@bot.command(name='info', aliases=['i'], help='Informations générales.')
async def show(ctx):
    # donne des informations générales sur le serveurs, les systèmes, le joueur et ses personnages
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
    # fonction qui oriente chaque système vers le bon système de lancé
    config = get_config()
    user = get_user(ctx)
    character = get_character(ctx)
    system = get_system(ctx)

    if character is None : await ctx.send("Vous n'utilisez actuellement aucun personnage."); return
    if system is None : await ctx.send("Vous n'utilisez actuellement aucun système de jeu."); return

    test = test.lower()

    if system == "TFTL" : await rollTFTL(ctx,config,user,character,system,test,mod); return

    else : await defaultRoll(ctx,config,user,character,system,test,mod); return

@bot.command(name='carac', help='Liste toutes les caractéristiques disponibles pour le personnage.')
async def carac(ctx):
    # affiche toutes les caractéristiques du personnage courant
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
    #utilisable uniquement par moi
    if not ctx.author.name == "Menchrof" : await ctx.send("Vous n'avez pas la permission d'effectuer cette commande."); return
    # tue le processus courant
    await quitter(ctx)
    sys.exit(1)

@bot.command(name='update', help='Met le bot à jour.')
async def update_bot(ctx):
    # utilisable uniquement par moi
    if not ctx.author.name == "Menchrof" : await ctx.send("Vous n'avez pas la permission d'effectuer cette commande."); return
    # enregistre le fichier de données en cas de problème
    shutil.copy("./config.json","./backup/backup_config.json")
    # relance le bot mais dans un autre processus
    subprocess.Popen("main.exe", shell=True)
    await ctx.message.add_reaction('👍')
    # tue le processus courant
    await quitter(ctx)
    sys.exit() # ligne de sécurité au cas où la fonction quitter disfonctionnerait


@bot.command(name='up', help='test')
async def up(ctx,*varargs):
    await ctx.send("Je suis up.")
    try:
        fl = float(varargs[0])
        await mpme(fl)
    except Exception as e : pass

@bot.command(name='dice', aliases=['d'], help='Lance des dés [n°dés]d[n°faces]')
async def dice(ctx,dice:str):
    # lancer de dés simple, permet d'avoir X dés et Y faces, par contre très sensibles à la syntaxe
    dice = dice.lower()
    dices, faces = map(int,dice.split('d'))

    li = []
    for i in range(dices):
        li.append(random.randint(1,faces))
    li = list(map(int,li))

    result = str(sum(li)) + '\n' + 'Details : ' + dice + " " + str(li)

    embed = discord.Embed()
    embed.add_field(name = "Résultats", value=result, inline=False)
    await ctx.send(embed=embed)

@bot.command(name="report", help="Use for report bug or way of improvements.")
async def report(ctx, *message:str):
    # fonction de report qui permet l'écriture dans le fichier report.txt
    # le bot m'envoie aussi un mp avec le message du report
    date = datetime.now()
    message = " ".join(message)
    message = str(date) + " : " + message
    message = ctx.author.name + " : " + message
    await mpme(message)
    message = message  + "\n"
    message = message.encode("UTF-8") # permet de passer du texte discord à un fichier lisible en utf-8
    with open("D:/perso/discordBot/jdr release/report.txt",'ab') as f: f.write(message)
    await ctx.send("Votre rapport a bien été enregistré, merci.")

@bot.command(name="connect", help="connect to a voice channel")
async def connect(ctx):
    # connecte le bot à une éventuelle channel vocale
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


@bot.command(name="disconnect", help="disconnect from voice channel")
async def disconnect(ctx):
    # déconnecte le bot d'une éventuelle channel vocale
    try:
        await ctx.voice_client.disconnect()
    except:
        pass

# se lance quand le bot se lance avec l'exécution du bot run token
@bot.event
async def on_ready():
    time.sleep(1)
    print('Connected to Discord!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,name='/help'))

@bot.event
# permet de modifier les embeds d'aides en accédant à des sous catégories présentes dans le fichier help.json
async def on_reaction_add(reaction,user):
    if user.id == 778899886087077909 : return
    if not (reaction.emoji in REACTIONS_DOC) : return
    text = {}
    with open("./help.json",'r',encoding='utf-8') as json_file : text = json.load(json_file)
    key = list(text.keys())[REACTIONS_DOC.index(reaction.emoji)]
    embed = discord.Embed(title=key)
    for key,value in text[key].items():
        embed.add_field(name=key, value=value, inline=False)
    await reaction.message.edit(embed=embed)


@bot.event
async def on_voice_state_update(member, before, after):
    # cette fonction est appelée à chaque modification du status d'un membre dans un salon vocal
    # ici on ne détecte que la réactivation du micro ou le changement de channel en ayant le micro activé
    # cette fonctionnalité c'est active qu'après 17 heures
    if member.id == 778899886087077909 : return # self
    if member.id == 234395307759108106 : return # groovy
    if member.id == 235088799074484224 : return # rythm
    if not (before.channel != after.channel) : return
    if after.channel.id == 671029269597650988 : await jingle(member.id, after.channel); return
    if (6 < datetime.today().hour and datetime.today().hour < 17) : return
    await jingle(member.id, after.channel)


# gestion de toutes les erreurs
# les erreurs sont envoyées directement dans les channels
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error,commands.errors.ClientException):
        await ctx.send(error)
    else:
        print(error)
        await ctx.send(error)


# lance le bot
bot.run(TOKEN)