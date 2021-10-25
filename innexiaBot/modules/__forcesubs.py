# credits @InukaAsith, @Mr_dark_prince

import logging
import time

from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired,
    PeerIdInvalid,
    UsernameNotOccupied,
    UserNotParticipant,
)
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup

from innexiaBot import DRAGONS as SUDO_USERS
from innexiaBot import pbot
from innexiaBot.modules.sql_extended import forceSubscribe_sql as sql

logging.basicConfig(level=logging.INFO)

static_data_filter = filters.create(
    lambda _, __, query: query.data == "onUnMuteRequest"
)


@pbot.on_callback_query(static_data_filter)
def _onUnMuteRequest(client, cb):
    user_id = cb.from_user.id
    chat_id = cb.message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        channel = chat_db.channel
        chat_member = client.get_chat_member(chat_id, user_id)
        if chat_member.restricted_by:
            if chat_member.restricted_by.id == (client.get_me()).id:
                try:
                    client.get_chat_member(channel, user_id)
                    client.unban_chat_member(chat_id, user_id)
                    cb.message.delete()
                    # if cb.message.reply_to_message.from_user.id == user_id:
                    # cb.message.delete()
                except UserNotParticipant:
                    client.answer_callback_query(
                        cb.id,
                        text=f"❗Ei membro em comum, Junte-se ao nosso @{channel} canal e imprensa 'UnMute Me' botão para digitar aqui no grupo.",
                        show_alert=True,
                    )
            else:
                client.answer_callback_query(
                    cb.id,
                    text="❗ Você foi silenciado por administradores devido a alguma outra razão.",
                    show_alert=True,
                )
        else:
            if (
                not client.get_chat_member(chat_id, (client.get_me()).id).status
                == "administrator"
            ):
                client.send_message(
                    chat_id,
                    f"❗ **{cb.from_user.mention} está tentando unMute-se, mas eu não posso desmute-lo porque eu não sou um administrador neste bate-papo me adicionar como administrador novamente.**\n__#Deixando esse bate-papo ademir 😭...__",
                )

            else:
                client.answer_callback_query(
                    cb.id,
                    text="❗ Aviso! Não aperte o botão quando você digitar.",
                    show_alert=True,
                )


@pbot.on_message(filters.text & ~filters.private & ~filters.edited, group=1)
def _check_member(client, message):
    chat_id = message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        user_id = message.from_user.id
        if (
            not client.get_chat_member(chat_id, user_id).status
            in ("administrator", "creator")
            and not user_id in SUDO_USERS
        ):
            channel = chat_db.channel
            try:
                client.get_chat_member(channel, user_id)
            except UserNotParticipant:
                try:
                    sent_message = message.reply_text(
                        "Bem vindo gay {} 🙏 \n **Você não se juntou ao nosso @{} Canal ainda** 😭 \n \nPor favor, junte-se [😪 Entra aí pu favor](https://t.me/{}) e bater o **UNMUTE ME** Botão. \n \n ".format(
                            message.from_user.mention, channel, channel
                        ),
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        "Inscreva-se no Canal",
                                        url="https://t.me/{}".format(channel),
                                    )
                                ],
                                [
                                    InlineKeyboardButton(
                                        "UnMute Me", callback_data="onUnMuteRequest"
                                    )
                                ],
                            ]
                        ),
                    )
                    client.restrict_chat_member(
                        chat_id, user_id, ChatPermissions(can_send_messages=False)
                    )
                except ChatAdminRequired:
                    sent_message.edit(
                        "❗ **Grave Sad manager não é administrador aqui..**\n__Dê-me permissões de proibição e repita.. \n#Terminando FSub...__"
                    )

            except ChatAdminRequired:
                client.send_message(
                    chat_id,
                    text=f"❗ **Eu não sou um administrador de @{channel} canal.**\n__Dê-me admin desse canal e repita.\n#Saindo do vosso FSub...__",
                )


@pbot.on_message(filters.command(["forcesubscribe", "fsub"]) & ~filters.private)
def config(client, message):
    user = client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status is "creator" or user.user.id in SUDO_USERS:
        chat_id = message.chat.id
        if len(message.command) > 1:
            input_str = message.command[1]
            input_str = input_str.replace("@", "")
            if input_str.lower() in ("off", "no", "disable"):
                sql.disapprove(chat_id)
                message.reply_text("❌ **A assinatura da força é desativada com sucesso.**")
            elif input_str.lower() in ("clear"):
                sent_message = message.reply_text(
                    "**Desmutando todos os membros que são silenciados por mim...**"
                )
                try:
                    for chat_member in client.get_chat_members(
                        message.chat.id, filter="restricted"
                    ):
                        if chat_member.restricted_by.id == (client.get_me()).id:
                            client.unban_chat_member(chat_id, chat_member.user.id)
                            time.sleep(1)
                    sent_message.edit("✅ **UnMuted todos os membros que são silenciados por mim.**")
                except ChatAdminRequired:
                    sent_message.edit(
                        "❗ **Eu não sou um administrador neste bate-papo.**\n__Eu não posso desmutar membros porque Eu não sou um administrador neste bate-papo me fazer administrador com a permissão do usuário proibição.__"
                    )
            else:
                try:
                    client.get_chat_member(input_str, "me")
                    sql.add_channel(chat_id, input_str)
                    message.reply_text(
                        f"✅ **O Force Subscribe está ativado**\n__Force Subscribe está ativado, todos os membros do grupo têm que assinar isso [Canal](https://t.me/{input_str}) a fim de enviar mensagens neste grupo.__",
                        disable_web_page_preview=True,
                    )
                except UserNotParticipant:
                    message.reply_text(
                        f"❗ **Não é um administrador no Canal**\n__Eu não sou um administrador no [Canal](https://t.me/{input_str}). Adicione-me como administrador para habilitar o ForceSubscribe.__",
                        disable_web_page_preview=True,
                    )
                except (UsernameNotOccupied, PeerIdInvalid):
                    message.reply_text(f"❗ **Nome de usuário do canal inválido.**")
                except Exception as err:
                    message.reply_text(f"❗ **ERROR Ademir:** ```{err}```")
        else:
            if sql.fs_settings(chat_id):
                message.reply_text(
                    f"✅ **Force Subscribe está ativado neste chat.**\n__Por isso [Canal](https://t.me/{sql.fs_settings(chat_id).channel})__",
                    disable_web_page_preview=True,
                )
            else:
                message.reply_text("❌ **Force Subscribe está desativado neste chat.**")
    else:
        message.reply_text(
            "❗ **Criador do grupo necessário**\n__Você tem que ser o criador do grupo para fazer isso.__"
        )


__help__ = """
*Force Subscribe:*
♦️ Grave Sad Manager pode silenciar membros que não são inscritos em seu canal até que eles se inscrevam
♦️ Quando ativado, silenciarei membros inscritos e mostrarei-lhes um botão sem ímute. Quando eles apertarem o botão eu vou desmute-los
*Configuração*
*Apenas criador*
⚙️ Adicione-me em seu grupo como administrador
⚙️ Adicione-me em seu canal como administrador 
 
*Comandos*
 ♦️ /fsub {channel username} - Para ligar e configurar o canal.
  💡 Faça isso primeiro...
 ♦️ /fsub - Para obter as configurações atuais.
 ♦️ /fsub disable - Para virar o ForceSubscrever..
  💡 Se você desativar fsub, você precisa definir novamente para o trabalho.. /fsub {channel username} 
 ♦️ /fsub clear - Para desmutar todos os membros que silenciaram por mim.
"""
__mod_name__ = "F-Sub"
