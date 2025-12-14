import requests
import os
import time

ERLC_API_KEY = os.getenv("ERLC_API_KEY")
WEBHOOK_URL = os.getenv("https://discord.com/api/webhooks/1449783614291316757/9y9QSsAfDH1gsfvt3YXdGjexEuGAQ155a0UN7kLw9YvVTvdpVOoOrcOMNpvyGJtBH4M6")

BASE_URL = "https://api.policeroleplay.community/v1"

DANGEROUS_COMMANDS = [
    "ban all",
    "kick all",
    "kill all",
    "load all",
    "jail all"
]

HEADERS = {
    "Authorization": f"Bearer {ERLC_API_KEY}",
    "Content-Type": "application/json"
}

def get_command_logs():
    return requests.get(
        f"{BASE_URL}/server/commandlogs",
        headers=HEADERS,
        timeout=10
    ).json()

def get_bans():
    return requests.get(
        f"{BASE_URL}/server/bans",
        headers=HEADERS,
        timeout=10
    ).json()

def send_webhook(message):
    requests.post(
        WEBHOOK_URL,
        json={"content": message},
        timeout=10
    )

seen = set()
print("ERLC detector running...")

while True:
    try:
        logs = get_command_logs()
        if "logs" not in logs:
            time.sleep(5)
            continue

        for log in logs["logs"]:
            if log["id"] in seen:
                continue
            seen.add(log["id"])

            cmd = log["command"].lower()
            user = log["username"]

            for bad in DANGEROUS_COMMANDS:
                if bad in cmd:
                    bans = get_bans()
                    players = []

                    if "bans" in bans:
                        for b in bans["bans"]:
                            players.append(
                                f"- `{b.get('username')}` (`{b.get('userId')}`)"
                            )

                    msg = (
                        "🚨 **ERLC RAID DETECTED** 🚨\n"
                        f"User: `{user}`\n"
                        f"Command: `{cmd}`\n\n"
                        "**Banned players:**\n" +
                        ("\n".join(players[:40]) or "None")
                    )

                    send_webhook(msg)

        time.sleep(5)

    except Exception as e:
        send_webhook(f"❌ ERLC detector error: `{e}`")
        time.sleep(10)
