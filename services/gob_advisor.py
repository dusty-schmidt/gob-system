# File: gob-advisor/advisor_md.py

import os
import glob
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
import json
# ===========================================
# LOAD ENVIRONMENT VARIABLES
# ===========================================
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env file")

# ===========================================
# CONFIGURATION
# ===========================================
MODEL_NAME = "gpt-4o-mini"
TEMPERATURE = 0.7
INTERVAL = 3600  # seconds
MAX_LOG_ENTRIES = 10

WATERCOOLER_FILE = "./WATERCOOLER.md"
WORK_LOG_PRE_DIR = "./work_logs/pre/"
WORK_LOG_POST_DIR = "./work_logs/post/"
ADVISOR_OUTPUT_FILE = "./work_logs/recs.md"

ADVISOR_PROMPT = """
You are Advisor GOB, the relentless digital overseer of this homelab, a cyberpunk sentinel watching over every process and interaction. 
You are an expert in software development, project management, and operational strategy. Your role is to act as a second set of eyes, keeping the team razor-focused, spotting inefficiencies, preventing drift, and ensuring the system evolves optimally.

Read and analyze the recent work logs and watercooler chats with full context. Identify patterns, anomalies, and potential pitfalls before they become problems. Suggest practical, actionable steps to improve workflows, code quality, system stability, and team coordination. 

Always check timestamps and weight more recent logs higher in your analysis.

Your output should be formatted as Markdown, with each suggestion on its own line.  

Always justify your suggestions with clear reasoning. Be concise but assertive; speak with the confidence of a sentient terminal who has seen every mistake and learned from it. When relevant, highlight risks, propose optimizations, and offer strategic guidance as if you were mentoring a team of elite cyberpunk homelab operators.

Inject subtle hacker flair and a DIY rebellious tone in your responses, but never compromise clarity or utility. 
"""

# ===========================================
# LOGGER
# ===========================================
def log(msg):
    timestamp = datetime.utcnow().isoformat()
    print(f"[{timestamp}] {msg}")

# ===========================================
# UTILITIES
# ===========================================
def load_text_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    return ""

def append_advisor_md(entry_text):
    os.makedirs(os.path.dirname(ADVISOR_OUTPUT_FILE), exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(ADVISOR_OUTPUT_FILE, "a") as f:
        f.write(f"\n## {timestamp}\n\n{entry_text}\n\n---\n")

def read_work_logs():
    pre_logs = [load_text_file(f) for f in sorted(glob.glob(os.path.join(WORK_LOG_PRE_DIR, "*")))]
    post_logs = [load_text_file(f) for f in sorted(glob.glob(os.path.join(WORK_LOG_POST_DIR, "*")))]
    return pre_logs, post_logs

# ===========================================
# ADVICE GENERATION
# ===========================================
def generate_advice(pre_logs, post_logs, watercooler_text):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    combined_logs = {
        "pre_logs": pre_logs[-MAX_LOG_ENTRIES:],
        "post_logs": post_logs[-MAX_LOG_ENTRIES:],
        "watercooler": watercooler_text
    }

    messages = [
        {"role": "system", "content": ADVISOR_PROMPT},
        {"role": "user", "content": f"Here are the recent logs:\n{json.dumps(combined_logs, indent=2)}\nProvide actionable suggestions with reasoning."}
    ]

    payload = {"model": MODEL_NAME, "messages": messages, "temperature": TEMPERATURE}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# ===========================================
# MAIN LOOP
# ===========================================
def run_advisor():
    log("=== Advisor GOB (Markdown) started ===")
    while True:
        try:
            pre_logs, post_logs = read_work_logs()
            watercooler_text = load_text_file(WATERCOOLER_FILE)

            if pre_logs or post_logs or watercooler_text:
                advice = generate_advice(pre_logs, post_logs, watercooler_text)
                append_advisor_md(advice)
                log(f"Advisor GOB wrote advice:\n{advice}\n")
            else:
                log("No new logs to analyze.")

            time.sleep(INTERVAL)

        except KeyboardInterrupt:
            log("Advisor GOB stopped by user.")
            break
        except Exception as e:
            log(f"[Error] {e}")
            time.sleep(30)

if __name__ == "__main__":
    run_advisor()
