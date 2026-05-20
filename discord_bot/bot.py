import discord
import os
import re
import requests
import unicodedata

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GITHUB_REPO  = os.environ.get('GITHUB_REPO', 'beomjinkim2000/Sprint_First_Proj')

AUTHOR_MAP = {
    '유재열': '유재열(Model)',
    '김범진': '김범진(PM)',
    '박창준': '박창준(Exp)',
    '황원재': '황원재(Data)',
}

def resolve_author(nickname: str) -> str:
    for key, val in AUTHOR_MAP.items():
        if key in nickname:
            return val
    return nickname

def nfc(s: str) -> str:
    return unicodedata.normalize('NFC', s)

@client.event
async def on_ready():
    print(f'Bot ready: {client.user}')

@client.event
async def on_message(message):
    # 봇 메시지 무시
    if message.author.bot:
        return
    # 답장이 아니면 무시
    if not message.reference:
        return

    try:
        original = await message.channel.fetch_message(message.reference.message_id)
    except Exception:
        return

    # Q&A 알림 메시지인지 확인
    if '새 질문이 등록됐어요' not in original.content:
        return

    # 제목 추출 → 파일명 복원
    m = re.search(r'\*\*제목:\*\*\s*(.+)', original.content)
    if not m:
        return

    title    = nfc(m.group(1).strip())
    qna_stem = nfc(f'[Q&A]-{title}')
    author   = resolve_author(message.author.display_name)
    answer   = message.content.strip()

    # GitHub Actions 트리거
    resp = requests.post(
        f'https://api.github.com/repos/{GITHUB_REPO}/dispatches',
        headers={
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json',
        },
        json={
            'event_type': 'discord-answer',
            'client_payload': {
                'qna_stem': qna_stem,
                'answer':   answer,
                'author':   author,
            },
        },
        timeout=10,
    )

    if resp.status_code == 204:
        await message.add_reaction('✅')
        print(f'Dispatched: {qna_stem} by {author}')
    else:
        await message.add_reaction('❌')
        print(f'Dispatch failed: {resp.status_code} {resp.text}')

client.run(os.environ['DISCORD_TOKEN'])
