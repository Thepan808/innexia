import os

#Saavn 

import requests
import wget
from pyrogram import filters

from innexiaBot import pbot as Jebot
from innexiaBot.pyrogramee.dark import get_arg


@Jebot.on_message(filters.command("saavn"))
async def song(client, message):
    message.chat.id
    message.from_user["id"]
    args = get_arg(message) + " " + "song"
    if args.startswith(" "):
        await message.reply("<b>Digite o nome da música❗</b>")
        return ""
    m = await message.reply_text(
        "Baixando sua música,\nAguarde ademir 🧐"
    )
    try:
        r = requests.get(f"https://jostapi.herokuapp.com/saavn?query={args}")
    except Exception as e:
        await m.edit(str(e))
        return
    sname = r.json()[0]["song"]
    slink = r.json()[0]["media_url"]
    ssingers = r.json()[0]["singers"]
    file = wget.download(slink)
    ffile = file.replace("mp4", "m4a")
    os.rename(file, ffile)
    await message.reply_audio(audio=ffile, title=sname, performer=ssingers)
    os.remove(ffile)
    await m.delete()


#deezer#
# Credits for @TheHamkerCat

import os
import aiofiles
import aiohttp
from pyrogram import filters
from innexiaBot import pbot as innexia

ARQ = "https://thearq.tech/"

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            try:
                data = await resp.json()
            except:
                data = await resp.text()
    return data

async def download_song(url):
    song_name = f"asuna.mp3"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(song_name, mode="wb")
                await f.write(await resp.read())
                await f.close()
    return song_name


@innexia.on_message(filters.command("deezer"))
async def deezer(_, message):
    if len(message.command) < 2:
        await message.reply_text("Baixe Agora via Deezer")
        return
    text = message.text.split(None, 1)[1]
    query = text.replace(" ", "%20")
    m = await message.reply_text("Procurando...")
    try:
        r = await fetch(f"{ARQ}deezer?query={query}&count=1")
        title = r[0]["title"]
        url = r[0]["url"]
        artist = r[0]["artist"]
    except Exception as e:
        await m.edit(str(e))
        return
    await m.edit("Baixando...")
    song = await download_song(url)
    await m.edit("Carregando fela da pota...")
    await message.reply_audio(audio=song, title=title, performer=artist)
    os.remove(song)
    await m.delete()

#Deezer
# Credits for @TheHamkerCat

import os
import aiofiles
import aiohttp
from pyrogram import filters
from innexiaBot import pbot as ASUNA

ARQ = "https://thearq.tech/"

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            try:
                data = await resp.json()
            except:
                data = await resp.text()
    return data

async def download_song(url):
    song_name = f"asuna.mp3"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(song_name, mode="wb")
                await f.write(await resp.read())
                await f.close()
    return song_name


@innexia.on_message(filters.command("deezer"))
async def deezer(_, message):
    if len(message.command) < 2:
        await message.reply_text("Baixe Agora Deezer")
        return
    text = message.text.split(None, 1)[1]
    query = text.replace(" ", "%20")
    m = await message.reply_text("Procurando...")
    try:
        r = await fetch(f"{ARQ}deezer?query={query}&count=1")
        title = r[0]["title"]
        url = r[0]["url"]
        artist = r[0]["artist"]
    except Exception as e:
        await m.edit(str(e))
        return
    await m.edit("Baixando...")
    song = await download_song(url)
    await m.edit("Carregando ademir...")
    await message.reply_audio(audio=song, title=title, performer=artist)
    os.remove(song)
    await m.delete()
    
    
__mod_name__ = "Music"

__help__ = """
• `/song`** <artista - nome da música (opcional)>: baixar a música em sua melhor qualidade disponível.(API BASED)
• `/video`** <artista - nome da música (opcional)>: baixar a música de vídeo em sua melhor qualidade disponível.
• `/deezer`** <Nome da música>: Baixar via deezer
• `/lyrics`** <Nome da música>: envia a letra completa da canção fornecida como entrada
• `/glyrics`** <i> Nome da música </i> : Este plugin busca letras de música com nome da música e artista.
"""

