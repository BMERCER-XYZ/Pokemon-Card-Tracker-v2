import os
import requests
import json
from datetime import datetime, timedelta, timezone

CARDS_FILE = "cards.txt"
DATA_JSON = "data.json"
HISTORICAL_JSON = "historical.json"

def price_fetch(pid):
    url = f"https://mpapi.tcgplayer.com/v2/product/{pid}/pricepoints"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()

def extract_foil_price(data, pid=None):
    # Exception for 616824: use "Normal" printing type
    if pid == "616824":
        for item in data:
            if item.get("printingType") == "Normal":
                return item.get("marketPrice")
        return None
    # Default: use "Foil"
    for item in data:
        if item.get("printingType") == "Foil":
            return item.get("marketPrice")
    return None

def load_historical_data():
    """Load existing historical data"""
    try:
        with open(HISTORICAL_JSON, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_historical_data(historical_data):
    """Save updated historical data"""
    with open(HISTORICAL_JSON, 'w') as f:
        json.dump(historical_data, f, indent=2)

def main():
    owners = {}
    historical_data = load_historical_data()
    
    # Calculate Adelaide time (UTC+9:30) to ensure consistent dating
    # When the action runs at 17:30 UTC, it's 3:00 AM next day in Adelaide
    utc_now = datetime.now(timezone.utc)
    adelaide_time = utc_now + timedelta(hours=9, minutes=30)
    today = adelaide_time.strftime('%Y-%m-%d')
    
    print(f"🕐 Current UTC time: {utc_now}")
    print(f"🇦🇺 Adelaide time: {adelaide_time}")
    print(f"📅 Using date: {today}")
    
    with open(CARDS_FILE, "r") as f:
        for line_num, line in enumerate(f, 1):
            try:
                pid, user, name = map(str.strip, line.strip().split(",", 2))
                response_data = price_fetch(pid)
                foil_info = extract_foil_price(response_data, pid)
                
                card_entry = {
                    "pid": pid,
                    "name": name,
                    "foil_price": foil_info
                }
                owners.setdefault(user, []).append(card_entry)
                
                # Add to historical data if price exists
                if foil_info is not None:
                    if pid not in historical_data:
                        historical_data[pid] = []
                    
                    # Check if we already have data for today
                    existing_today = any(entry['date'] == today for entry in historical_data[pid])
                    if not existing_today:
                        historical_data[pid].append({
                            'price': foil_info,
                            'date': today
                        })
                
                print(f"✅ Line {line_num}: {user} - {card_entry}")

            except ValueError:
                print(f"⚠️ Line {line_num}: Skipping malformed line: {line.strip()}")
            except requests.RequestException as e:
                print(f"❌ Line {line_num}: API error - {e}")

    # Save current prices
    with open(DATA_JSON, "w") as file:
        json.dump(owners, file, indent=2)
    
    # Save historical data
    save_historical_data(historical_data)
    
    print(f"✅ Updated {DATA_JSON} and {HISTORICAL_JSON}")

if __name__ == "__main__":
    main()

