# link_core.py

import json
import os
import uuid
import time
from datetime import datetime, time as dt_time # Keep your datetime imports

# --- Vercel KV (Redis) Client Initialization ---
KV_URL = os.getenv('KV_URL') # You manually set this in Vercel project settings
kv_client = None

if KV_URL:
    try:
        import redis # Ensure redis is imported only if KV_URL exists
        kv_client = redis.from_url(KV_URL)
        kv_client.ping()
        print("Successfully connected to Vercel KV in link_core.py!")
    except ImportError:
        print("The 'redis' library is not installed. Please add it to requirements.txt.")
        kv_client = None
    except Exception as e:
        print(f"Error connecting to Vercel KV in link_core.py: {e}")
        kv_client = None
else:
    print("KV_URL environment variable not found. KV store functionality will be disabled. Using local file fallback (not recommended for Vercel).")

# Define keys for storing data in KV
LINKS_DATA_KEY = "interactive_link_manager:links"
CONFIG_DATA_KEY = "interactive_link_manager:config"

# Fallback file paths for local development if KV is not available
# These will NOT work for persistence on Vercel.
LOCAL_DATA_FILE = "links.json"
LOCAL_CONFIG_FILE = "config.json"

# --- Configuration Management ---
CONFIG = {} # Global CONFIG variable
DEFAULT_CONFIG = {
    "page_size": 20,
    "date_format_choice": "1",
    "date_formats": {
        "1": "%Y-%m-%d %H:%M:%S",
        "2": "%d/%m/%Y %H:%M",
        "3": "%m/%d/%y %I:%M %p"
    },
    "default_export_path": "~/"
}

def load_config():
    global CONFIG
    if kv_client:
        try:
            config_json = kv_client.get(CONFIG_DATA_KEY)
            if config_json:
                loaded_config = json.loads(config_json)
                # Ensure all default keys are present
                for key, value in DEFAULT_CONFIG.items():
                    loaded_config.setdefault(key, value)
                CONFIG = loaded_config
                print("Config loaded from Vercel KV.")
                return
            else:
                print("No config found in Vercel KV, using default and saving.")
                CONFIG = DEFAULT_CONFIG.copy()
                save_config() # Save default to KV
                return
        except Exception as e:
            print(f"Error loading config from Vercel KV: {e}. Using default and attempting to save.")
            CONFIG = DEFAULT_CONFIG.copy()
            save_config() # Attempt to save default to KV
            return
    else: # Fallback to local file if KV client is not available (for local dev)
        print("KV client not available. Attempting to load config from local file (for local dev ONLY).")
        if not os.path.exists(LOCAL_CONFIG_FILE):
            CONFIG = DEFAULT_CONFIG.copy()
            _save_config_local() # Save to local file
            return
        try:
            with open(LOCAL_CONFIG_FILE, 'r') as f:
                loaded_config = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                loaded_config.setdefault(key, value)
            CONFIG = loaded_config
        except Exception as e:
            print(f"Warning: Error loading local config: {e}. Using default settings.")
            CONFIG = DEFAULT_CONFIG.copy()

def save_config():
    global CONFIG
    if kv_client:
        try:
            kv_client.set(CONFIG_DATA_KEY, json.dumps(CONFIG))
            print("Config saved to Vercel KV.")
            return True
        except Exception as e:
            print(f"Error: Could not save configuration to Vercel KV: {e}")
            return False
    else: # Fallback for local dev
        print("KV client not available. Attempting to save config to local file (for local dev ONLY).")
        return _save_config_local()

def _save_config_local(): # Helper for local file saving
    global CONFIG
    try:
        with open(LOCAL_CONFIG_FILE, 'w') as f:
            json.dump(CONFIG, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving local config: {e}")
        return False


def get_active_date_format_str():
    global CONFIG
    if not CONFIG: load_config() # Ensure config is loaded
    choice = CONFIG.get("date_format_choice", "1")
    date_formats_dict = CONFIG.get("date_formats", DEFAULT_CONFIG["date_formats"])
    return date_formats_dict.get(choice, DEFAULT_CONFIG["date_formats"]["1"])


# --- Link Data Management (Using Vercel KV) ---
def _load_links_from_kv():
    if not kv_client:
        print("KV client not available in _load_links_from_kv. Falling back to local file (for local dev ONLY).")
        return _load_links_local() # Fallback for local dev
    try:
        links_json = kv_client.get(LINKS_DATA_KEY)
        if links_json:
            links_data = json.loads(links_json)
            # Your existing logic for ensuring default fields in links
            for link in links_data:
                link.setdefault('id', str(uuid.uuid4()))
                link.setdefault('url', '')
                link.setdefault('title', link.get('url', 'N/A'))
                link.setdefault('notes', '')
                link.setdefault('is_default', False)
                link.setdefault('reminder_timestamp', 0)
                link.setdefault('last_visited_timestamp', 0)
                link.setdefault('visit_count', 0)
                link.setdefault('created_timestamp', int(time.time()))
            return links_data
        return [] # No data in KV, return empty list
    except Exception as e:
        print(f"Error loading links from Vercel KV: {e}. Returning empty list.")
        return []

def _save_links_to_kv(links_data_list):
    if not kv_client:
        print("KV client not available in _save_links_to_kv. Falling back to local file (for local dev ONLY).")
        return _save_links_local(links_data_list) # Fallback for local dev
    try:
        kv_client.set(LINKS_DATA_KEY, json.dumps(links_data_list))
        print(f"Saved {len(links_data_list)} links to Vercel KV.")
        return True
    except Exception as e:
        print(f"Error saving links to Vercel KV: {e}")
        return False

# --- Local file fallbacks (for development when KV_URL is not set) ---
def _load_links_local():
    if not os.path.exists(LOCAL_DATA_FILE): return []
    try:
        if os.path.getsize(LOCAL_DATA_FILE) == 0: return []
        with open(LOCAL_DATA_FILE, 'r') as f:
            links_data = json.load(f)
        # ... (your existing default field logic from original load_links_data) ...
        for link in links_data:
            link.setdefault('id', str(uuid.uuid4())) # etc.
        return links_data
    except Exception as e:
        print(f"Warning: Error loading local links: {e}")
        return []

def _save_links_local(links_data_list):
    try:
        with open(LOCAL_DATA_FILE, 'w') as f:
            json.dump(links_data_list, f, indent=4)
        return True
    except Exception as e:
        print(f"ERROR saving local links: {e}")
        return False

# --- Core Link Operations (Now use _load_links_from_kv and _save_links_to_kv) ---
def get_all_links():
    return _load_links_from_kv() # Changed

def add_new_link(url, title, notes, is_default, reminder_timestamp):
    links = _load_links_from_kv() # Changed
    normalized_url = url.strip()
    for existing_link in links:
        if existing_link.get('url', '').strip() == normalized_url:
            return "duplicate_url"
    new_link = {
        "id": str(uuid.uuid4()), "url": normalized_url,
        "title": title.strip() if title.strip() else normalized_url,
        "notes": notes.strip(), "is_default": is_default,
        "reminder_timestamp": reminder_timestamp if reminder_timestamp else 0,
        "last_visited_timestamp": 0, "visit_count": 0,
        "created_timestamp": int(time.time())
    }
    links.append(new_link)
    if _save_links_to_kv(links): # Changed
        return new_link
    else:
        return None

def get_link_by_id(link_id):
    links = _load_links_from_kv() # Changed
    for link in links:
        if link.get('id') == link_id:
            return link
    return None

def update_link(link_id, updated_data):
    links = _load_links_from_kv() # Changed
    link_found = False
    updated_link_details = None
    for i, link in enumerate(links):
        if link.get('id') == link_id:
            # Your existing update logic for link keys
            for key, value in updated_data.items():
                link[key] = value # Ensure you only update valid keys
            links[i] = link # Update the link in the list
            updated_link_details = link
            link_found = True
            break
    if link_found and _save_links_to_kv(links): # Changed
        return updated_link_details
    elif not link_found:
        print(f"Error: Link with ID {link_id} not found for update.")
    return None

def delete_link_by_id(link_id):
    all_links = _load_links_from_kv() # Changed
    if all_links is None: return False # Should ideally not happen if _load_links_from_kv returns [] on error
    original_length = len(all_links)
    links_to_keep = [link for link in all_links if link.get('id') != link_id]
    if len(links_to_keep) < original_length:
        if _save_links_to_kv(links_to_keep): # Changed
            return True
        else:
            return False
    else:
        return False # Link not found

def record_link_visit(link_id):
    links = _load_links_from_kv() # Changed
    link_to_update = None
    for current_link in links:
        if current_link.get('id') == link_id:
            link_to_update = current_link
            break
    if link_to_update:
        link_to_update.setdefault('visit_count', 0) # Ensure keys exist before incrementing
        link_to_update.setdefault('last_visited_timestamp', 0)
        link_to_update['visit_count'] += 1
        link_to_update['last_visited_timestamp'] = int(time.time())
        if _save_links_to_kv(links): # Changed
            return True
        else:
            return False
    else:
        return False

# --- Your existing helper functions (format_web_timestamp, get_daily_time_status, search, sort) ---
# These should largely remain the same as they operate on the data after it's loaded.
# Make sure they use the global CONFIG variable which is now loaded from KV.

def format_web_timestamp(ts):
    global CONFIG
    if not CONFIG: load_config() # Ensure config is loaded
    if not ts or ts == 0: return "N/A"
    date_format_str = get_active_date_format_str()
    try:
        return datetime.fromtimestamp(ts).strftime(date_format_str)
    except (ValueError, OSError):
        return "Invalid Date"

def get_daily_time_status(reminder_timestamp):
    # This function seems fine as is, assuming reminder_timestamp is correct
    if not reminder_timestamp or reminder_timestamp == 0:
        return {'display_time': "N/A", 'status': "n_a"}
    try:
        reminder_datetime_obj = datetime.fromtimestamp(reminder_timestamp)
        hour_12 = reminder_datetime_obj.strftime('%I')
        if hour_12.startswith('0'):
            hour_12 = hour_12[1:]
        display_time = f"{hour_12}:{reminder_datetime_obj.strftime('%M %p')}"
        now = datetime.now()
        reminder_time_of_day = reminder_datetime_obj.time()
        # Check if reminder_datetime_obj's date is today, or if it's just a time
        # For simplicity, assuming reminder_timestamp is an absolute point in time
        if reminder_datetime_obj < now:
            status = "elapsed" # Changed from "elapsed_today" for clarity if ts is absolute
        else:
            status = "upcoming" # Changed from "upcoming_today"
        return {'display_time': display_time, 'status': status}
    except (ValueError, OSError) as e:
        print(f"Error processing reminder timestamp {reminder_timestamp}: {e}")
        return {'display_time': "Invalid Date", 'status': "n_a"}

# --- Search and Sort Logic (no changes needed here for KV, they work on the loaded list) ---
def core_search_links(all_links, search_term, search_type="basic", criteria=None):
    # ... your existing code ...
    filtered = []
    if search_type == "basic":
        st_lower = search_term.lower()
        for link in all_links:
            if st_lower in link.get('title', '').lower() or \
               st_lower in link.get('url', '').lower() or \
               st_lower in link.get('notes', '').lower():
                filtered.append(link)
    return filtered

def core_sort_links(links_to_sort, sort_by, sort_order):
    # ... your existing complex sorting code ...
    # This operates on the list in memory, so no direct KV changes needed.
    sorted_list = list(links_to_sort)
    if sort_by:
        reverse = (sort_order == 'desc')
        if sort_by == 'title':
            sorted_list.sort(key=lambda x: x.get('title','').lower(), reverse=reverse)
        elif sort_by == 'created':
            sorted_list.sort(key=lambda x: x.get('created_timestamp',0), reverse=reverse)
        # ... other sort conditions from your original code ...
        elif sort_by == 'reminder_time':
             sorted_list.sort(key=lambda x: x.get('reminder_timestamp', float('-inf') if reverse else float('inf')), reverse=reverse)

    return sorted_list


# Load config when this module is imported
# This will attempt to load from KV first, then local file (for dev), then defaults.
load_config()

