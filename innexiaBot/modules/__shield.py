#    Copyright (C) DevsExpo 2020-2021
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


import asyncio
import os
import re

import better_profanity
import emoji
import nude
import requests
from better_profanity import profanity
from google_trans_new import google_translator
from telethon import events
from telethon.tl.types import ChatBannedRights

from innexiaBot import BOT_ID
from innexiaBot.conf import get_int_key, get_str_key

# from innexiaBot.db.mongo_helpers.nsfw_guard import add_chat, get_all_nsfw_chats, is_chat_in_db, rm_chat
from innexiaBot.pyrogramee.telethonbasics import is_admin
from innexiaBot.events import register
from innexiaBot import MONGO_DB_URI 
from pymongo import MongoClient
from innexiaBot.modules.sql_extended.nsfw_watch_sql import (
    add_nsfwatch,
    get_all_nsfw_enabled_chat,
    is_nsfwatch_indb,
    rmnsfwatch,
)
from innexiaBot import telethn as tbot

translator = google_translator()
MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)

MONGO_DB_URI = get_str_key("MONGO_DB_URI")

client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["innexiaBot"]

async def is_nsfw(event):
    lmao = event
    if not (
        lmao.gif
        or lmao.video
        or lmao.video_note
        or lmao.photo
        or lmao.sticker
        or lmao.media
    ):
        return False
    if lmao.video or lmao.video_note or lmao.sticker or lmao.gif:
        try:
            starkstark = await event.client.download_media(lmao.media, thumb=-1)
        except:
            return False
    elif lmao.photo or lmao.sticker:
        try:
            starkstark = await event.client.download_media(lmao.media)
        except:
            return False
    img = starkstark
    f = {"file": (img, open(img, "rb"))}

    r = requests.post("https://starkapi.herokuapp.com/nsfw/", files=f).json()
    if r.get("success") is False:
        is_nsfw = False
    elif r.get("is_nsfw") is True:
        is_nsfw = True
    elif r.get("is_nsfw") is False:
        is_nsfw = False
    return is_nsfw


@tbot.on(events.NewMessage(pattern="/gshield (.*)"))
async def nsfw_watch(event):
    if not event.is_group:
        await event.reply("Você só pode desativar Nsfw em grupos.")
        return
    input_str = event.pattern_match.group(1)
    if not await is_admin(event, BOT_ID):
        await event.reply("`Eu deveria ser administrador para fazer isso!`")
        return
    if await is_admin(event, event.message.sender_id):
        if (
            input_str == "on"
            or input_str == "On"
            or input_str == "ON"
            or input_str == "enable"
        ):
            if is_nsfwatch_indb(str(event.chat_id)):
                await event.reply("`Este chat já habilitou o relógio Nsfw.`")
                return
            add_nsfwatch(str(event.chat_id))
            await event.reply(
                f"**Bate-papo adicionado {event.chat.title} Com ID {event.chat_id} Para banco de dados. Este conteúdo nsfw que aparecerá no grupo será excluído**"
            )
        elif (
            input_str == "off"
            or input_str == "Off"
            or input_str == "OFF"
            or input_str == "disable"
        ):
            if not is_nsfwatch_indb(str(event.chat_id)):
                await event.reply("Este chat não habilitou o relógio Nsfw.")
                return
            rmnsfwatch(str(event.chat_id))
            await event.reply(
                f"**Chat removido {event.chat.title} Com ID {event.chat_id} Da Nsfw Watch**"
            )
        else:
            await event.reply(
                "Eu desembrulhei `/nsfwguardian on` e `/nsfwguardian off` somente"
            )
    else:
        await event.reply("`Você deve ser administrador para fazer isso!`")
        return


@tbot.on(events.NewMessage())
async def ws(event):
    warner_starkz = get_all_nsfw_enabled_chat()
    if len(warner_starkz) == 0:
        return
    if not is_nsfwatch_indb(str(event.chat_id)):
        return
    if not (event.photo):
        return
    if not await is_admin(event, BOT_ID):
        return
    if await is_admin(event, event.message.sender_id):
        return
    sender = await event.get_sender()
    await event.client.download_media(event.photo, "nudes.jpg")
    if nude.is_nude("./nudes.jpg"):
        await event.delete()
        st = sender.first_name
        hh = sender.id
        final = f"**NSFW DETECTADO seu filho da puta**\n\n{st}](tg://user?id={hh}) sua mensagem contém conteúdo NSFW.. Então, Grave Manager apagou a mensagem\n\n **Nsfw Remetente - User / Bot :** {st}](tg://user?id={hh})  \n\n`🧐 Detecções automáticas By Grave Manager AI` \n**#GROUP_GUARDIAN** "
        dev = await event.respond(final)
        await asyncio.sleep(10)
        await dev.delete()
        os.remove("nudes.jpg")


"""
@pbot.on_message(filters.command("nsfwguardian") & ~filters.edited & ~filters.bot)
async def add_nsfw(client, message):
    if len(await member_permissions(message.chat.id, message.from_user.id)) < 1:
        await message.reply_text("**Você não tem permissões suficientes.**")
        return
    status = message.text.split(None, 1)[1] 
    if status == "on" or status == "ON" or status == "enable":
        pablo = await message.reply("`Processamento..`")
        if is_chat_in_db(message.chat.id):
            await pablo.edit("Este chat já está no meu DB")
            return
        me = await client.get_me()
        add_chat(message.chat.id)
        await pablo.edit("Bate-papo com sucesso ao relógio NSFW.")
        
    elif status == "off" or status=="OFF" or status == "disable":
        pablo = await message.reply("`Processamento..`")
        if not is_chat_in_db(message.chat.id):
            await pablo.edit("Este chat não está no dB.")
            return
        rm_chat(message.chat.id)
        await pablo.edit("Chat removido com sucesso do serviço de relógio NSFW")
    else:
        await message.reply(" Use apenas `/nsfwguardian on` or `/nsfwguardian off` somente")
        
@pbot.on_message(filters.incoming & filters.media & ~filters.private & ~filters.channel & ~filters.bot)
async def nsfw_watch(client, message):
    lol = get_all_nsfw_chats()
    if len(lol) == 0:
        message.continue_propagation()
    if not is_chat_in_db(message.chat.id):
        message.continue_propagation()
    hot = await is_nsfw(client, message)
    if not hot:
        message.continue_propagation()
    else:
        try:
            await message.delete()
        except:
            pass
        lolchat = await client.get_chat(message.chat.id)
        ctitle = lolchat.title
        if lolchat.username:
            hehe = lolchat.username
        else:
            hehe = message.chat.id
        midhun = await client.get_users(message.from_user.id)
        await message.delete()
        if midhun.username:
            Escobar = midhun.username
        else:
            Escobar = midhun.id
        await client.send_message(
            message.chat.id,
            f"**NSFW DETECTADO**\n\n{hehe}'s mensagem contêm conteúdo NSFW.. Então, Eu apaguei a mensagem\n\n **Nsfw Remetente - User / Bot :** `{Escobar}` \n**Chat Título:** `{ctitle}` \n\n`🧐 Detecções automáticas By Grave Manager AI` \n**#GROUP_GUARDIAN** ",
        )
        message.continue_propagation()
"""


# This Module is ported from https://github.com/MissJuliaRobot/MissJuliaRobot
# This hardwork was completely done by MissJuliaRobot
# Full Credits goes to MissJuliaRobot


approved_users = db.approve
spammers = db.spammer
globalchat = db.globchat

CMD_STARTERS = "/"
profanity.load_censor_words_from_file("./profanity_wordlist.txt")


@register(pattern="^/profanity(?: |$)(.*)")
async def profanity(event):
    if event.fwd_from:
        return
    if not event.is_group:
        await event.reply("Você só pode profanidade em grupos.")
        return
    event.pattern_match.group(1)
    if not await is_admin(event, BOT_ID):
        await event.reply("`Eu deveria ser administrador para fazer isso!`")
        return
    if await is_admin(event, event.message.sender_id):
        input = event.pattern_match.group(1)
        chats = spammers.find({})
        if not input:
            for c in chats:
                if event.chat_id == c["id"]:
                    await event.reply(
                        "Por favor, forneça alguma entrada sim ou não (yes or no) .\n\nConfiguração atual é : **on**"
                    )
                    return
            await event.reply(
                "Por favor, forneça alguma entrada sim ou não.\n\nConfiguração atual é : **off**"
            )
            return
        if input == "on":
            if event.is_group:
                chats = spammers.find({})
                for c in chats:
                    if event.chat_id == c["id"]:
                        await event.reply(
                            "Filtro de profanação já está ativado para este bate-papo."
                        )
                        return
                spammers.insert_one({"id": event.chat_id})
                await event.reply("Filtro de profanidade ligado para este bate-papo.")
        if input == "off":
            if event.is_group:
                chats = spammers.find({})
                for c in chats:
                    if event.chat_id == c["id"]:
                        spammers.delete_one({"id": event.chat_id})
                        await event.reply("Filtro de profanação desligado para este bate-papo.")
                        return
            await event.reply("Filtro de profanação não está ligado para este bate-papo.")
        if not input == "on" and not input == "off":
            await event.reply("Eu só entendo por on or off")
            return
    else:
        await event.reply("`Você deve ser administrador para fazer isso!`")
        return


@register(pattern="^/globalmode(?: |$)(.*)")
async def profanity(event):
    if event.fwd_from:
        return
    if not event.is_group:
        await event.reply("Você só pode ativar o relógio do modo global em grupos.")
        return
    event.pattern_match.group(1)
    if not await is_admin(event, BOT_ID):
        await event.reply("`Eu deveria ser administrador para fazer isso!`")
        return
    if await is_admin(event, event.message.sender_id):

        input = event.pattern_match.group(1)
        chats = globalchat.find({})
        if not input:
            for c in chats:
                if event.chat_id == c["id"]:
                    await event.reply(
                        "Por favor, forneça alguma entrada sim ou não.\n\nConfiguração atual é : **on**"
                    )
                    return
            await event.reply(
                "Por favor, forneça alguma entrada sim ou não.\n\nConfiguração atual é : **off**"
            )
            return
        if input == "on":
            if event.is_group:
                chats = globalchat.find({})
                for c in chats:
                    if event.chat_id == c["id"]:
                        await event.reply(
                            "O modo global já está ativado para este bate-papo."
                        )
                        return
                globalchat.insert_one({"id": event.chat_id})
                await event.reply("Modo global ligado para este bate-papo.")
        if input == "off":
            if event.is_group:
                chats = globalchat.find({})
                for c in chats:
                    if event.chat_id == c["id"]:
                        globalchat.delete_one({"id": event.chat_id})
                        await event.reply("Modo global desligado para este bate-papo.")
                        return
            await event.reply("O modo global não está ligado para este bate-papo.")
        if not input == "on" and not input == "off":
            await event.reply("Eu só entendo on ou off")
            return
    else:
        await event.reply("`Você deve ser administrador para fazer isso!`")
        return


@tbot.on(events.NewMessage(pattern=None))
async def del_profanity(event):
    if event.is_private:
        return
    msg = str(event.text)
    sender = await event.get_sender()
    # let = sender.username
    if await is_admin(event, event.message.sender_id):
        return
    chats = spammers.find({})
    for c in chats:
        if event.text:
            if event.chat_id == c["id"]:
                if better_profanity.profanity.contains_profanity(msg):
                    await event.delete()
                    if sender.username is None:
                        st = sender.first_name
                        hh = sender.id
                        final = f"[{st}](tg://user?id={hh}) **{msg}** é detectado como um NSFW e sua mensagem foi excluída"
                    else:
                        final = f"Sir **{msg}** é detectado como um NSFW e sua mensagem foi excluída"
                    dev = await event.respond(final)
                    await asyncio.sleep(10)
                    await dev.delete()
        if event.photo:
            if event.chat_id == c["id"]:
                await event.client.download_media(event.photo, "nudes.jpg")
                if nude.is_nude("./nudes.jpg"):
                    await event.delete()
                    st = sender.first_name
                    hh = sender.id
                    final = f"**NSFW DETECTADO**\n\n{st}](tg://user?id={hh}) sua mensagem contém conteúdo NSFW.. Então, Eu apaguei a mensagem\n\n **Nsfw Remetente - User / Bot :** {st}](tg://user?id={hh})  \n\n`🧐 Detecções automáticas By Grave ManagerAI` \n**#GROUP_GUARDIAN** "
                    dev = await event.respond(final)
                    await asyncio.sleep(10)
                    await dev.delete()
                    os.remove("nudes.jpg")


def extract_emojis(s):
    return "".join(c for c in s if c in emoji.UNICODE_EMOJI)


@tbot.on(events.NewMessage(pattern=None))
async def del_profanity(event):
    if event.is_private:
        return
    msg = str(event.text)
    sender = await event.get_sender()
    # sender.username
    if await is_admin(event, event.message.sender_id):
        return
    chats = globalchat.find({})
    for c in chats:
        if event.text:
            if event.chat_id == c["id"]:
                u = msg.split()
                emj = extract_emojis(msg)
                msg = msg.replace(emj, "")
                if (
                    [(k) for k in u if k.startswith("@")]
                    and [(k) for k in u if k.startswith("#")]
                    and [(k) for k in u if k.startswith("/")]
                    and re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []
                ):
                    h = " ".join(filter(lambda x: x[0] != "@", u))
                    km = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", h)
                    tm = km.split()
                    jm = " ".join(filter(lambda x: x[0] != "#", tm))
                    hm = jm.split()
                    rm = " ".join(filter(lambda x: x[0] != "/", hm))
                elif [(k) for k in u if k.startswith("@")]:
                    rm = " ".join(filter(lambda x: x[0] != "@", u))
                elif [(k) for k in u if k.startswith("#")]:
                    rm = " ".join(filter(lambda x: x[0] != "#", u))
                elif [(k) for k in u if k.startswith("/")]:
                    rm = " ".join(filter(lambda x: x[0] != "/", u))
                elif re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []:
                    rm = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", msg)
                else:
                    rm = msg
                # print (rm)
                b = translator.detect(rm)
                if not "en" in b and not b == "":
                    await event.delete()
                    st = sender.first_name
                    hh = sender.id
                    final = f"[{st}](tg://user?id={hh}) you should only speak in english here !"
                    dev = await event.respond(final)
                    await asyncio.sleep(10)
                    await dev.delete()
#

__help__ = """
<b> Group Guardian: </b>
✪ Grave Manager pode proteger seu grupo de remetentes NSFW, usuários de palavras escória e também pode forçar os membros a usar inglês

<b>Comandos</b>
 - /gshield <i>on/off</i> - Habilitar| Desativar a limpeza porno
 - /globalmode <i>on/off</i> - Habilitar| Desativar o modo somente inglês
 - /profanity <i>on/off</i> - Habilitar| Desativar a limpeza de palavras escória
 

 
"""
__mod_name__ = "Shield"
