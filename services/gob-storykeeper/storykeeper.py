import json
import time
import requests
import os
import re
import toml
from datetime import datetime, timezone
from dotenv import load_dotenv

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))

# File Paths
CONFIG_FILE = os.path.join(SCRIPT_DIR, "storykeeper_config.toml")
STATE_FILE = os.path.join(SCRIPT_DIR, "storykeeper_state.json")
WATERCOOLER_FILE = os.path.join(PROJECT_ROOT, "WATERCOOLER.md")
STORY_FILE = os.path.join(PROJECT_ROOT, "STORIES.md")
ENV_FILE = os.path.join(PROJECT_ROOT, '.env')

# --- Load .env for API Key ---
load_dotenv(dotenv_path=ENV_FILE)
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "gpt-4o-mini"

def log(msg):
    """Prints a timestamped log."""
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"[{timestamp}] {msg}")

def load_config():
    """Loads settings from the TOML config file."""
    log(f"Loading configuration from {CONFIG_FILE}")
    try:
        with open(CONFIG_FILE, 'r') as f:
            return toml.load(f)
    except (FileNotFoundError, toml.TomlDecodeError) as e:
        log(f"Error loading config file: {e}. Exiting.")
        exit(1)

def load_state():
    """Loads the last processed timestamp from the state file."""
    log(f"Loading state from {STATE_FILE}")
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            return state.get("last_processed_timestamp")
    except (FileNotFoundError, json.JSONDecodeError):
        log("State file not found or invalid. Will process all entries.")
        return None

def save_state(timestamp_str):
    """Saves the latest processed timestamp to the state file."""
    log(f"Saving new state. Last processed timestamp: {timestamp_str}")
    with open(STATE_FILE, 'w') as f:
        json.dump({"last_processed_timestamp": timestamp_str}, f, indent=2)

def parse_watercooler_entries(file_path, last_timestamp_str):
    """
    Parses the WATERCOOLER.md file, filters for new entries, and returns them in chronological order.
    """
    log(f"Parsing {file_path} for new entries.")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        log(f"Source file not found: {file_path}")
        return [], None

    # Regex to find entries like "## 2025-09-08 04:45:00 - DS"
    entry_pattern = re.compile(r"(^##\s*(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}).*?)(?=^##\s*\d{4}-\d{2}-\d{2}|\\Z)", re.S | re.M)
    
    entries = []
    for match in entry_pattern.finditer(content):
        entry_text = match.group(1).strip()
        timestamp_str = match.group(2)
        entry_dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        entries.append((entry_dt, entry_text))

    if not entries:
        log("No entries found in watercooler file.")
        return [], None

    # Filter for new entries
    last_processed_dt = datetime.fromisoformat(last_timestamp_str).replace(tzinfo=timezone.utc) if last_timestamp_str else datetime.min.replace(tzinfo=timezone.utc)
    new_entries = [entry for entry in entries if entry[0] > last_processed_dt]

    if not new_entries:
        log("No new entries to process since last run.")
        return [], None

    # Sort new entries chronologically (they should already be, but this is a safeguard)
    new_entries.sort()
    
    log(f"Found {len(new_entries)} new entries to process.")
    
    latest_timestamp = new_entries[-1][0].isoformat()
    combined_text = "\n\n---\n\n".join([entry[1] for entry in new_entries])
    
    return combined_text, latest_timestamp

def generate_story(content, config):
    """Generates a story using the OpenRouter API."""
    log("Generating story from new content...")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    messages = [
        {"role": "system", "content": config["SYSTEM_PROMPT"]},
        {"role": "user", "content": f"Here are the latest entries:\n\n{content}"}
    ]
    
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": config["TEMPERATURE"]
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def append_story_to_file(story_text):
    """Appends the generated story to the main STORIES.md file."""
    log(f"Appending new story to {STORY_FILE}")
    try:
        with open(STORY_FILE, "a", encoding='utf-8') as f:
            f.write(f"# Story from {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write(f"{story_text}\n\n---\n\n")
        log("Successfully wrote new story.")
    except Exception as e:
        log(f"Error writing to story file: {e}")

def main():
    """Main execution loop."""
    config = load_config()
    interval = config.get("INTERVAL_SECONDS", 86400)
    
    log("=== Storykeeper Service Started ===")
    log(f"Update interval set to {interval} seconds.")

    while True:
        try:
            last_timestamp = load_state()
            new_content, latest_timestamp = parse_watercooler_entries(WATERCOOLER_FILE, last_timestamp)
            
            if new_content and latest_timestamp:
                story = generate_story(new_content, config)
                append_story_to_file(story)
                save_state(latest_timestamp)
            
            log(f"Sleeping for {interval} seconds...")
            time.sleep(interval)
        except KeyboardInterrupt:
            log("Storykeeper stopped by user.")
            break
        except Exception as e:
            log(f"[ERROR] An unexpected error occurred: {e}")
            log("Waiting 60 seconds before retrying.")
            time.sleep(60)

if __name__ == "__main__":
    main()