from pyrogram import Client, filters
import requests
import json
import time
import os 
import random
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
###############################################################################################
api_id = "20308839"
api_hash = "f210fd3cda2dc5246d4fe8ea3e498c4f"
bot_token = "6886346876:AAHeeML0MtRZ5nouBC3bPUR8vDObqOm1Eo8"
owner_id = 5402391081
app = Client("renapbot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
users_file = os.path.join("db", "users.js")
users_db_path = "db/users.js"
banned_users_db_path = "db/banned_users.json"
###############################################################################################
def load_users():
    try:
        with open(users_db_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
def save_users(users):
    with open(users_db_path, 'w') as file:
        json.dump(users, file, indent=4)
def find_user(users, user_id):
    for user in users:
        if user["id"] == user_id:
            return user
    return None
def fetch_data(dni):
    api_url = f"https://clientes.credicuotas.com.ar/v1/onboarding/resolvecustomers/{dni}"
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.RequestException:
        return None
def get_sexo_from_api(dni):
    url = f"https://clientes.credicuotas.com.ar/v1/onboarding/resolvecustomers/{dni}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("sexo")
    return None
def load_banned_users():
    try:
        with open(banned_users_db_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_banned_users(banned_users):
    with open(banned_users_db_path, "w") as file:
        json.dump(banned_users, file)
###############################################################################################
banned_users = load_banned_users()
###############################################################################################
@app.on_message(filters.command("cd", prefixes=["/", "$", ".", ",", "!"]))
def check_banned_users(client, message):
    if message.from_user.id in banned_users:
        message.reply("You are banned from the bot and cannot use commands.")
        return
def fetch_customer_data(client, message):
    try:
        users = load_users()
        user_id = message.from_user.id
        user = find_user(users, user_id)
        if user is None or user["tokens"] <= 0:
            message.reply("You don't have tokens. Please purchase more tokens with @elmasketocee.")
            return
        if len(message.command) < 2:
            message.reply("You didn't enter a DNI.")
            return
        dni = message.command[1]
        message.reply("The API is processing your request...")
        response_data = fetch_data(dni)
        if response_data:
            data = response_data[0]
            nombre = data["nombrecompleto"]
            dni = data["dni"]
            genero = "MASCULINO" if data["sexo"] == "M" else "FEMENINO"
            cuit = data["cuit"]
            usuario = message.from_user.username if message.from_user.username else "UsuarioDesconocido"
            user["tokens"] -= 1
            save_users(users)
            response_text = (
                f"t.me/elmasketocee 🔍\n\n"
                f"```[>>>]``` Información Personal\n"
                f"ℹ️ | Resultados.\n"
                f"```\n> Nombre: {nombre}\n\n"
                f"> DNI: {dni}\n\n"
                f"> Genero: {genero}\n\n"
                f"> CUIT: {cuit}\n```\n\n"
                f"> Solicitud by: @{usuario}\n"
                f"[<<<] Dev: @elmasketocee"
            )
            message.reply(response_text)
        else:
            error_message = "Oh, Renapersito encountered an error. Please try using another command. Don't worry, I won't deduct tokens."
            message.reply(error_message)
            client.send_message(owner_id, f"Error accessing the API with DNI: {dni}.\nUser: @{message.from_user.username if message.from_user.username else 'UnknownUser'}\nError message to user: {error_message}")
    except IndexError:
        error_message = "You didn't enter a DNI."
        message.reply(error_message)
        client.send_message(owner_id, f"Unexpected error: {error_message}\nUser: @{message.from_user.username if message.from_user.username else 'UnknownUser'}")
    except Exception as e:
        error_message = "Oh, Renapersito tuvo un error. Prueba usar otro comando o habla con mi creador..."
        message.reply(error_message)
        client.send_message(owner_id, f"Unexpected error: {str(e)}\nUser: @{message.from_user.username if message.from_user.username else 'UnknownUser'}\nError message to user: {error_message}")
###############################################################################################
@app.on_message(filters.command("addtk", prefixes=["/", "$", ".", ",", "!"]))
def add_tokens(client, message):
    if message.from_user.id != owner_id:
        message.reply("... How you do know about this command?")
        return
    if len(message.command) < 3:
        message.reply("You forgot to provide the user ID and the number of tokens to add.")
        return
    target_id = int(message.command[1])
    try:
        cantidad = int(message.command[2])
    except ValueError:
        message.reply("The number of tokens must be an integer.")
        return
    users = load_users()
    user = find_user(users, target_id)
    if user:
        user["tokens"] += cantidad
        save_users(users)
        message.reply(f"{cantidad} tokens successfully added to user with ID {target_id}.")
    else:
        message.reply(f"No user found with ID {target_id}.")
###############################################################################################
@app.on_message(filters.command("subtk", prefixes=["/", "$", ".", ",", "!"]))
def subtract_tokens(client, message):
    if message.from_user.id != owner_id:
        message.reply("WTF, como conoces este comando?")
        return
    if len(message.command) < 3:
        message.reply("Please provide the user ID and the number of tokens to subtract.")
        return
    target_id = int(message.command[1])
    try:
        cantidad = int(message.command[2])
    except ValueError:
        message.reply("The number of tokens must be an integer.")
        return
    users = load_users()
    user = find_user(users, target_id)
    if user:
        if user["tokens"] >= cantidad:
            user["tokens"] -= cantidad
            save_users(users)
            message.reply(f"{cantidad} tokens successfully subtracted from user with ID {target_id}.")
        else:
            message.reply(f"User with ID {target_id} does not have enough tokens.")
    else:
        message.reply(f"No user found with ID {target_id}.")
###############################################################################################
@app.on_message(filters.command("cmds", prefixes=["/", "$", ".", ",", "!"]))
def list_commands(client, message):
    if message.from_user.id in banned_users:
        message.reply("You are banned from the bot and cannot use commands.")
        return
    commands_list = (
        "🔧 Available Commands:\n\n"
        "/cd {dni} - Basic DNI query.\n"
        "/fi {dni {sexo} - Fiscal query.\n"
        "/me - Displays information about your plan\n"
        "[<<<] Dev: @elmasketocee"
    )
    message.reply(commands_list)
###############################################################################################
@app.on_message(filters.command("fi", prefixes=["/", "$", ".", ",", "!"]))
def check_banned_users(client, message):
    if message.from_user.id in banned_users:
        message.reply("You are banned from the bot and cannot use commands.")
        return
def fetch_license(client, message):
    try:
        args = message.text.split()
        if len(args) < 2:
            message.reply("You forgot the DNI.")
            return

        dni = args[1]
        sexo = args[2] if len(args) > 2 else get_sexo_from_api(dni)

        if not sexo:
            message.reply("You didn't enter the sex. | M or F")
            return

        api_url = f"https://fiscalizar.seguridadvial.gob.ar/api/licencias?numeroDocumento={dni}&sexo={sexo}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()

            if isinstance(data, list) and data:
                all_licenses_info = ""
                for licencia in data:
                    licencia_info = (
                        "<code>[XXX] | Informacion Personal</code>\n\n"
                        f"<code>>_ Nombre:</code> <code>{licencia.get('nombre', 'N/A')}</code>\n"
                        f"<code>>_ Apellido:</code> <code>{licencia.get('apellido', 'N/A')}</code>\n"
                        f"<code>>_ Nacionalidad:</code> <code>{licencia.get('nacionalidad', 'N/A')}</code>\n"
                        f"<code>>_ Fecha de Nacimiento:</code> <code>{licencia.get('fechaNacimiento', 'N/A')}</code>\n\n"
                        f"<code>[XXX] | Informacion Licencia</code>\n\n"
                        f"<code>>_ Fecha de Emisión:</code> <code>{licencia.get('fechaEmision', 'N/A')}</code>\n"
                        f"<code>>_ Fecha de Vencimiento:</code> <code>{licencia.get('fechaVencimiento', 'N/A')}</code>\n"
                        f"<code>>_ Principiante:</code> <code>{'Sí' if licencia.get('principiante') else 'No'}</code>\n"
                        f"<code>>_ Lugar de Emisión:</code> <code>{licencia.get('lugarEmision', 'N/A')}</code>\n"
                        f"<code>>_ Provincia:</code> <code>{licencia.get('provincia', 'N/A')}</code>\n"
                        f"<code>>_ Localidad:</code> <code>{licencia.get('localidad', 'N/A')}</code>\n"
                        f"<code>>_ Clases Códigos:</code> <code>{licencia.get('clasesCodigos', 'N/A')}</code>\n"
                        f"<code>>_ Inhabilitada:</code> <code>{'Sí' if licencia.get('inhabilitada') else 'No'}</code>\n"
                        f"<code>>_ Vencida:</code> <code>{'Sí' if licencia.get('vencida') else 'No'}</code>\n\n"
                        f"[>>>] Dev: @elmasketocee \n"
                        f"[<<<] Request By: @{message.from_user.username}\n"
                    )
                    all_licenses_info += licencia_info
                message.reply(all_licenses_info.strip())
            else:
                message.reply("DNI, sin licencia >.<")
        else:
            message.reply("Error al consultar la API.")
    except Exception as e:
        message.reply(f"Se produjo un error: {str(e)}")
###############################################################################################
@app.on_message(filters.command("rena", prefixes=["/", "$", ".", ",", "!"]))
def check_banned_users(client, message):
    if message.from_user.id in banned_users:
        message.reply("You are banned from the bot and cannot use commands.")
        return
def fetch_rena_info(client, message):
    try:
        args = message.text.split()
        if len(args) < 2:
            message.reply("Required format: /rena {dni} {sex}")
            return
        dni = args[1]
        sexo = args[2] if len(args) > 2 else None
        if not dni:
            message.reply("You did not enter the DNI.")
            return
        if not sexo:
            message.reply("You did not enter the sex.")
            return
        api_url = f"https://api-rena-85qr.onrender.com/api/renaper/1?dni={dni}&sexo={sexo}"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()

            if data.get("codigo") == 99:
                mensaje = (
                    "<code>[XXX] | Informacion Personal</code>\n\n"
                    f"<code>>_ Apellido:</code> <code>{data.get('apellido', 'N/A')}</code>\n"
                    f"<code>>_ Nombres:</code> <code>{data.get('nombres', 'N/A')}</code>\n"
                    f"<code>>_ Fecha de Nacimiento:</code> <code>{data.get('fecha_nacimiento', 'N/A')}</code>\n"
                    f"<code>>_ CUIL:</code> <code>{data.get('cuil', 'N/A')}</code>\n"
                    f"<code>>_ Nacionalidad:</code> <code>{data.get('nacionalidad', 'N/A')}</code>\n\n"
                    
                    "<code>[XXX] | Informacion Domicilio</code>\n\n"
                    f"<code>>_ Calle:</code> <code>{data.get('calle', 'N/A')}</code>\n"
                    f"<code>>_ Número:</code> <code>{data.get('numero', 'N/A')}</code>\n"
                    f"<code>>_ Piso:</code> <code>{data.get('piso', 'N/A')}</code>\n"
                    f"<code>>_ Departamento:</code> <code>{data.get('departamento', 'N/A')}</code>\n"
                    f"<code>>_ Ciudad:</code> <code>{data.get('ciudad', 'N/A')}</code>\n"
                    f"<code>>_ Provincia:</code> <code>{data.get('provincia', 'N/A')}</code>\n"
                    f"<code>>_ País:</code> <code>{data.get('pais', 'N/A')}</code>\n\n"
                    
                    "<code>[XXX] | Informacion de Estado</code>\n\n"
                    f"<code>>_ Estado Fallecimiento:</code> <code>{data.get('mensaje_fallecido', 'N/A')}</code>\n"
                )
                message.reply(mensaje)
            else:
                message.reply("Incorrect format, please check.")
        else:
            message.reply("Error al consultar la API.")
    except Exception as e:
        message.reply(f"Se produjo un error: {str(e)}")
###############################################################################################
@app.on_message(filters.command("fuera", prefixes=["/", "$", ".", ",", "!"]))
def ban_user(client, message):
    if message.from_user.id != owner_id:
        message.reply("Dont Try again.")
        return
    if len(message.command) < 2:
        message.reply("USER ID, not found in message.")
        return
    target_id = int(message.command[1])
    if target_id not in banned_users:
        banned_users.append(target_id)
        save_banned_users(banned_users)
        message.reply(f"El usuario con ID {target_id} ha sido baneado del bot.")
    else:
        message.reply(f"User ID {target_id} is already banned.")
###############################################################################################
@app.on_message(filters.command("adentro", prefixes=["/", "$", ".", ",", "!"]))
def unban_user(client, message):
    if message.from_user.id != owner_id:
        message.reply("Dont Try Again.")
        return

    if len(message.command) < 2:
        message.reply("USER ID, not found in message.")
        return

    target_id = int(message.command[1])

    if target_id in banned_users:
        banned_users.remove(target_id)
        save_banned_users(banned_users)
        message.reply(f"USER ID {target_id} has been UN-Banned")
    else:
        message.reply(f"User ID {target_id} not exist in ban-list")
###############################################################################################
@app.on_message(filters.command("panel", prefixes=["/", "$", ".", ",", "!"]))
def admin_panel(client, message):
    if message.from_user.id != owner_id:
        message.reply("Dont Try Again.")
        return
    admin_commands = (
        "🔒 **Secrets Commands here hehe** 🔒\n\n"
        "/subtk - Quitar tokens a un usuario.\n"
        "/addtk - Añadir tokens a un usuario.\n"
        "/fuera - Banear a un usuario.\n"
        "/adentro - Desbanear a un usuario.\n"
    )
    message.reply(admin_commands)
###############################################################################################
@app.on_message(filters.command("me", prefixes=["/", "$", ".", ",", "!"]))
def show_user_info(client, message):
    user_id = message.from_user.id
    banned_users = load_banned_users()
    if user_id in banned_users:
        message.reply("You are Banned")
        return
    users = load_users()
    user_info = next((user for user in users if user["id"] == user_id), None)

    if user_info:
        user_message = (
            "👤 **About of You Person** 👤\n\n"
            f"**ID:** `{user_info['id']}`\n"
            f"**Usuario:** @{user_info['username']}\n"
            f"**Tokens:** `{user_info['tokens']}`\n"
        )
        message.reply(user_message)
    else:
        message.reply("You not are in my database, send /start to register.")
###############################################################################################
app.run()