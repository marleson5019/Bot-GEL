import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import os
import json
import base64

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_ID = 1478575347535581194
ADMIN_ROLE_ID = 1478575226366329044

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

google_credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
google_credentials_base64 = os.getenv("GOOGLE_CREDENTIALS_BASE64")
google_credentials_file = os.getenv(
    "GOOGLE_CREDENTIALS_FILE",
    "mimetic-scion-489519-s2-2caca6f1d60b.json"
)

if google_credentials_json:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(google_credentials_json), scope
    )
elif google_credentials_base64:
    decoded_json = base64.b64decode(google_credentials_base64).decode("utf-8")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(decoded_json), scope
    )
elif os.path.exists(google_credentials_file):
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        google_credentials_file, scope
    )
else:
    raise RuntimeError(
        "Credenciais do Google ausentes. Defina GOOGLE_CREDENTIALS_JSON "
        "(ou GOOGLE_CREDENTIALS_BASE64) no ambiente de deploy."
    )

client = gspread.authorize(creds)
sheet = client.open(os.getenv("GOOGLE_SHEET_NAME", "Database-GEL-Teste")).sheet1


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")


# BOAS VINDAS
@bot.event
async def on_member_join(member):

    canal = discord.utils.get(member.guild.text_channels, name="📌boas-vindas")

    if canal:
        await canal.send(
            f"👋 Bem-vindo ao servidor {member.mention}!\n\n"
            f"Para acessar o servidor vá até o canal <#1478571542202810521> e utilize:\n"
            "`!verificar SUA_MATRICULA`\n\n"
            "Caso precise de ajuda utilize:\n"
            "`!ajuda` no mesmo canal."
        )


# LISTA DE COMANDOS
@bot.command()
async def comandos(ctx):

    embed = discord.Embed(
        title="📜 Comandos do servidor",
        description="Lista de comandos disponíveis",
        color=0x00ff88
    )

    embed.add_field(
        name="🔹 Comandos",
        value=(
            "`!verificar MATRICULA` → Verifica sua matrícula\n"
            "`!ajuda` → Abre ticket de suporte\n"
            "`!olimpiadas` → Canal oficial da Olimpíada\n"
            "`!insta` → Instagram oficial do GEL\n"
            "`!comandos` → Mostra esta lista"
        ),
        inline=False
    )

    embed.set_footer(text="Digite 'adm' para ver comandos administrativos")

    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        resposta = await bot.wait_for("message", timeout=30.0, check=check)

        if resposta.content.lower() == "adm":

            embed_admin = discord.Embed(
                title="🛠 Comandos Administrativos",
                color=0xff5555
            )

            embed_admin.add_field(
                name="Admin",
                value=(
                    "`!clear quantidade` → Limpa mensagens\n"
                    "`!closeticket` → Fecha um ticket"
                ),
                inline=False
            )

            await ctx.send(embed=embed_admin)

    except:
        pass


# LINK TELEGRAM OLIMPÍADAS
@bot.command()
async def olimpiadas(ctx):

    embed = discord.Embed(
        title="🏆 Olimpíadas do Campus",
        description="Entre no canal oficial de avisos das olimpíadas:",
        color=0x0099ff
    )

    embed.add_field(
        name="Telegram Oficial",
        value="https://t.me/+LYClMgGPZ7ozZWNh",
        inline=False
    )

    await ctx.send(embed=embed)


# INSTAGRAM GEL
@bot.command()
async def insta(ctx):

    embed = discord.Embed(
        title="📸 Instagram do GEL",
        description="Siga o perfil oficial do GEL:",
        color=0xff2e63
    )

    embed.add_field(
        name="Instagram",
        value="https://www.instagram.com/ifes.gel/",
        inline=False
    )

    await ctx.send(embed=embed)


@bot.command()
async def verificar(ctx, codigo):

    codigos = [c.lower() for c in sheet.col_values(2)]

    if codigo.lower() in codigos:

        role = ctx.guild.get_role(ROLE_ID)

        if role:
            await ctx.author.add_roles(role)
            await ctx.send("✅ Código válido! Você foi verificado.", delete_after=10)
        else:
            await ctx.send("❌ Cargo não encontrado.", delete_after=10)

    else:
        await ctx.send("❌ Código inválido.", delete_after=10)


@bot.command()
async def clear(ctx, quantidade: int = None):

    admin_role = ctx.guild.get_role(ADMIN_ROLE_ID)

    if admin_role not in ctx.author.roles:
        await ctx.send("❌ Você não tem permissão para usar esse comando.", delete_after=10)
        return

    await ctx.send("⚠️ Tem certeza que deseja limpar as mensagens? (s/n)", delete_after=15)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        resposta = await bot.wait_for("message", timeout=30.0, check=check)
    except:
        await ctx.send("⏱ Tempo esgotado.", delete_after=10)
        return

    if resposta.content.lower() != "s":
        await ctx.send("❌ Operação cancelada.", delete_after=10)
        return

    if quantidade:
        await ctx.channel.purge(limit=quantidade + 1)
    else:
        await ctx.channel.purge(limit=1000)

    await ctx.send("🧹 Mensagens apagadas.", delete_after=5)


# TICKET
@bot.command()
async def ajuda(ctx):

    admin_role = ctx.guild.get_role(ADMIN_ROLE_ID)

    for channel in ctx.guild.text_channels:
        if channel.name.startswith("ticket-"):
            if ctx.author in channel.members:
                await ctx.send("❌ Você já possui um ticket aberto.", delete_after=10)
                return

    await ctx.send("📩 Deseja abrir um ticket de suporte? (s/n)", delete_after=15)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        resposta = await bot.wait_for("message", timeout=30.0, check=check)
    except:
        await ctx.send("⏱ Tempo esgotado.", delete_after=10)
        return

    if resposta.content.lower() != "s":
        await ctx.send("❌ Operação cancelada.", delete_after=10)
        return

    numero = random.randint(1000, 9999)
    nome_canal = f"ticket-{numero}"

    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    canal = await ctx.guild.create_text_channel(nome_canal, overwrites=overwrites)

    await canal.send(
        f"👋 Olá {ctx.author.mention}!\n\n"
        "Aguarde que um administrador irá atendê-lo.\n\n"
        "Informe:\n"
        "- Nome completo\n"
        "- Matrícula\n"
        "- Turma\n"
        "- Sua dúvida"
    )

    await ctx.send(f"✅ Ticket criado: {canal.mention}")


# FECHAR TICKET
@bot.command()
async def closeticket(ctx):

    admin_role = ctx.guild.get_role(ADMIN_ROLE_ID)

    if admin_role not in ctx.author.roles:
        await ctx.send("❌ Você não tem permissão.", delete_after=10)
        return

    if not ctx.channel.name.startswith("ticket-"):
        await ctx.send("❌ Use este comando dentro de um ticket.", delete_after=10)
        return

    await ctx.send("⚠️ Tem certeza? (s/n)", delete_after=15)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        resposta = await bot.wait_for("message", timeout=30.0, check=check)
    except:
        return

    if resposta.content.lower() == "s":
        await ctx.send("🔒 Fechando ticket...", delete_after=5)
        await ctx.channel.delete()


discord_token = os.getenv("DISCORD_TOKEN")

if not discord_token:
    raise RuntimeError("Defina a variavel de ambiente DISCORD_TOKEN antes de iniciar o bot.")

bot.run(discord_token)