from flask import Flask
from threading import Thread
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import requests
import csv
import io
from typing import Literal

# ✅ Flask 앱 정의
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Discord Bot is running on fps.ms!"

# ✅ Flask 서버 실행 함수

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# ✅ Flask 서버를 백그라운드로 실행
Thread(target=run_flask).start()

# ✅ 디스코드 봇 설정
load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ✅ 슬래시 명령어 정의
@bot.tree.command(
    name="닉네임변경하기",
    description="사용자의 닉네임을 고유번호 · 닉네임 · 직업 형식으로 변경합니다.",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    사용자id="닉네임을 변경할 대상 사용자",
    고유번호="고유번호",
    닉네임="닉네임",
    직업="직업"
)
async def 닉네임변경하기(interaction: discord.Interaction, 사용자id: discord.Member, 고유번호: str, 닉네임: str, 직업: str):
    new_nick = f"{고유번호} / {닉네임} / {직업}"
    if len(new_nick) > 32:
        new_nick = new_nick[:32]
    try:
        await 사용자id.edit(nick=new_nick)
        embed = discord.Embed(title="✅ 닉네임 변경 성공", description=f"{사용자id.mention} 님의 닉네임이 변경되었습니다.", color=discord.Color.green())
        embed.add_field(name="새 닉네임", value=f"`{new_nick}`", inline=False)
        embed.set_footer(text=f"실행자: {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except discord.Forbidden:
        embed = discord.Embed(title="❌ 닉네임 변경 실패", description="권한 부족으로 닉네임을 변경할 수 없습니다.", color=discord.Color.red())
        embed.set_footer(text=f"실행자: {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        embed = discord.Embed(title="⚠️ 오류 발생", description=f"에러 내용:\n```{e}```", color=discord.Color.red())
        embed.set_footer(text=f"실행자: {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(
    name="역할추가",
    description="여러 개의 역할을 한 사용자에게 부여합니다.",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    멤버="역할을 줄 대상 멤버",
    역할1="첫 번째 역할",
    역할2="두 번째 역할 (선택)",
    역할3="세 번째 역할 (선택)",
    역할4="네 번째 역할 (선택)",
    역할5="다섯 번째 역할 (선택)"
)
async def 여러역할추가(interaction: discord.Interaction, 멤버: discord.Member, 역할1: discord.Role, 역할2: discord.Role = None, 역할3: discord.Role = None, 역할4: discord.Role = None, 역할5: discord.Role = None):
    역할들 = [역할 for 역할 in [역할1, 역할2, 역할3, 역할4, 역할5] if 역할 is not None]
    실패역할 = []
    성공역할 = []
    for 역할 in 역할들:
        if 역할 >= interaction.guild.me.top_role:
            실패역할.append(역할.name)
            continue
        try:
            await 멤버.add_roles(역할, reason=f"{interaction.user}에 의해 여러역할추가")
            성공역할.append(역할.name)
        except:
            실패역할.append(역할.name)
    embed = discord.Embed(title="📦 역할 추가 결과", color=discord.Color.green() if 성공역할 else discord.Color.red())
    embed.add_field(name="✅ 성공한 역할", value=", ".join(성공역할) if 성공역할 else "없음", inline=False)
    embed.add_field(name="❌ 실패한 역할", value=", ".join(실패역할) if 실패역할 else "없음", inline=False)
    embed.set_footer(text=f"명령 실행자: {interaction.user}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="임직원목록",
    description="요식팩토리 임직원 목록을 출력해요.",
    guild=discord.Object(id=GUILD_ID)
)
async def 임직원목록(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    try:
        url = "https://docs.google.com/spreadsheets/d/1IH1DQ7KI9LS2mInesJor3B7uz01oAhKWpVhFO8v3yh4/export?format=csv&gid=0"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            await interaction.followup.send("❌ 데이터를 불러오지 못했습니다. 상태 코드: " + str(response.status_code))
            return
        data = response.content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(data))
        embeds = []
        current_embed = discord.Embed(title="📋 요식팩토리 임직원 목록", color=discord.Color.blue())
        field_count = 0
        for row in reader:
            직급 = row.get("직급", "없음")
            부서 = row.get("부서", "없음")
            이름 = row.get("이름", "없음")
            current_embed.add_field(name=f"{직급} - {이름}", value=f"부서: {부서}", inline=False)
            field_count += 1
            if field_count >= 25:
                embeds.append(current_embed)
                current_embed = discord.Embed(title="📋 요식팩토리 임직원 목록 (계속)", color=discord.Color.blue())
                field_count = 0
        if field_count > 0:
            embeds.append(current_embed)
        for embed in embeds:
            await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"⚠️ 오류 발생: {e}")

@bot.tree.command(
    name="채팅",
    description="원하는 메시지를 보냅니다.",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(message="전송할 메시지")
async def 채팅(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(f"{message}")

@bot.tree.command(
    name="인증양식",
    description="로블록스 인증 정보를 임베드로 출력합니다.",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    로블록스닉네임="당신의 로블록스 닉네임",
    소속계열사="소속계열사를 선택하세요",
    방문경로="채용 합격 / 사장 초대 / 침입 중 하나 입력"
)
async def 인증양식(interaction: discord.Interaction, 로블록스닉네임: str, 소속계열사: Literal["장충동왕국밥", "인백스테이크하우스", "연화스시", "요식팩토리"], 방문경로: str):
    embed = discord.Embed(title="🛂 인증 양식", description="입력하신 정보는 아래와 같습니다.", color=discord.Color.blurple())
    embed.add_field(name="🔹 로블록스 닉네임", value=로블록스닉네임, inline=False)
    embed.add_field(name="🔹 소속계열사", value=소속계열사, inline=False)
    embed.add_field(name="🔹 방문 경로", value=방문경로, inline=False)
    embed.set_footer(text=f"제출자: {interaction.user}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# ✅ 봇 시작 시 슬래시 명령어 동기화
@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print("✅ 슬래시 명령어 동기화 완료")
    activity = discord.Game(name="구두 닦기")
    await bot.change_presence(status=discord.Status.online, activity=activity)

# ✅ 봇 실행 (에러 잡아서 Replit 죽지 않게 함)
try:
    bot.run(TOKEN)
except Exception as e:
    print("❌ Bot crashed:", e)
