# link_core.py

import json
import os
import uuid
import time 
from datetime import datetime, time as dt_time

DATA_FILE = "links.json"
CONFIG_FILE = "config.json"

# --- Configuration Management ---
CONFIG = {}
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
    if not os.path.exists(CONFIG_FILE):
        CONFIG = DEFAULT_CONFIG.copy()
        save_config()
        return
    try:
        with open(CONFIG_FILE, 'r') as f:
            loaded_config = json.load(f)
        for key, value in DEFAULT_CONFIG.items():
            loaded_config.setdefault(key, value)
        CONFIG = loaded_config
    except (IOError, json.JSONDecodeError) as e:
        print(f"Warning: Error loading config: {e}. Using default settings.")
        CONFIG = DEFAULT_CONFIG.copy()
    except Exception as e:
        print(f"Warning: Unexpected error loading config: {e}. Using default settings.")
        CONFIG = DEFAULT_CONFIG.copy()

def save_config():
    global CONFIG
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(CONFIG, f, indent=4)
        return True
    except IOError as e:
        print(f"Error: Could not save configuration: {e}")
        return False
    except Exception as e:
        print(f"Error: Unexpected error saving configuration: {e}")
        return False

def get_active_date_format_str():
    global CONFIG
    choice = CONFIG.get("date_format_choice", "1")
    date_formats_dict = CONFIG.get("date_formats", DEFAULT_CONFIG["date_formats"])
    return date_formats_dict.get(choice, DEFAULT_CONFIG["date_formats"]["1"])


# --- Link Data Management ---
def load_links_data(filepath=DATA_FILE):
    if not os.path.exists(filepath):
        if filepath == DATA_FILE: return []
        else: return None 
    try:
        if os.path.getsize(filepath) == 0: return []
        with open(filepath, 'r') as f:
            links_data = json.load(f)
        if not isinstance(links_data, list):
            print(f"Warning: Data in '{filepath}' is not a list.")
            return None if filepath != DATA_FILE else []
        
        if filepath == DATA_FILE:
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
    except (IOError, json.JSONDecodeError) as e:
        print(f"Warning: Error loading links from '{filepath}': {e}")
        return None if filepath != DATA_FILE else []
    except Exception as e:
        print(f"Warning: Unexpected error loading links from '{filepath}': {e}")
        return None if filepath != DATA_FILE else []


def save_links_data(links, filepath=DATA_FILE):
    # print(f"DEBUG: Attempting to save {len(links)} links to {filepath}") 
    try:
        with open(filepath, 'w') as f:
            json.dump(links, f, indent=4)
        # print(f"DEBUG: Successfully saved links to {filepath}")
        return True
    except IOError as e:
        print(f"ERROR in save_links_data (IOError): Could not save links to '{filepath}': {e}")
        return False
    except Exception as e:
        print(f"ERROR in save_links_data (Exception): Unexpected error saving links to '{filepath}': {e}")
        return False

# --- Core Link Operations ---
def get_all_links():
    return load_links_data()

def add_new_link(url, title, notes, is_default, reminder_timestamp):
    links = load_links_data()
    normalized_url = url.strip()
    for existing_link in links:
        if existing_link.get('url', '').strip() == normalized_url:
            # print(f"Attempt to add duplicate URL: {normalized_url}")
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
    if save_links_data(links):
        return new_link
    else:
        # print("Error: Failed to save links data after appending new link.")
        return None

def get_link_by_id(link_id):
    links = load_links_data()
    for link in links:
        if link.get('id') == link_id:
            return link
    return None

def update_link(link_id, updated_data):
    links = load_links_data()
    link_found = False
    updated_link_details = None
    for i, link in enumerate(links):
        if link.get('id') == link_id:
            for key, value in updated_data.items():
                if key in link: 
                    link[key] = value
            links[i] = link
            updated_link_details = link
            link_found = True
            break
    if link_found and save_links_data(links):
        return updated_link_details
    elif not link_found:
        print(f"Error: Link with ID {link_id} not found for update.")
    return None

def delete_link_by_id(link_id):
    # print(f"DEBUG: delete_link_by_id called for ID: {link_id}")
    all_links = load_links_data()
    if all_links is None:
        # print("DEBUG: load_links_data returned None in delete_link_by_id.")
        return False
    original_length = len(all_links)
    # print(f"DEBUG: Original link count: {original_length}")
    links_to_keep = [link for link in all_links if link.get('id') != link_id]
    if len(links_to_keep) < original_length:
        # print(f"DEBUG: Link {link_id} found and filtered. New list size: {len(links_to_keep)}. Attempting save.")
        if save_links_data(links_to_keep):
            # print(f"DEBUG: Link {link_id} successfully deleted and list saved.")
            return True
        else:
            # print(f"DEBUG: Link {link_id} filtered, but FAILED TO SAVE the updated list.")
            return False 
    else:
        # print(f"DEBUG: Link {link_id} not found in the list during delete_link_by_id. No deletion performed.")
        return False

def record_link_visit(link_id):
    links = load_links_data()
    link_to_update = None
    for current_link in links:
        if current_link.get('id') == link_id:
            link_to_update = current_link
            break
    if link_to_update:
        link_to_update.setdefault('visit_count', 0)
        link_to_update.setdefault('last_visited_timestamp', 0)
        link_to_update['visit_count'] += 1
        link_to_update['last_visited_timestamp'] = int(time.time())
        if save_links_data(links):
            return True
        else:
            # print(f"ERROR: Failed to save links data after updating visit for link ID {link_id}")
            return False
    else:
        # print(f"WARNING: Link ID {link_id} not found for recording visit (in record_link_visit).")
        return False

# --- Helper for formatting timestamps & daily time status ---
def format_web_timestamp(ts):
    global CONFIG 
    if not ts or ts == 0: return "N/A"
    date_format_str = get_active_date_format_str()
    try:
        return datetime.fromtimestamp(ts).strftime(date_format_str)
    except (ValueError, OSError):
        return "Invalid Date"

def get_daily_time_status(reminder_timestamp):
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
        reminder_for_today = now.replace(
            hour=reminder_time_of_day.hour,
            minute=reminder_time_of_day.minute,
            second=reminder_time_of_day.second,
            microsecond=0 
        )
        if reminder_for_today < now:
            status = "elapsed_today" 
        else:
            status = "upcoming_today" 
        return {'display_time': display_time, 'status': status}
    except (ValueError, OSError) as e:
        print(f"Error processing reminder timestamp {reminder_timestamp}: {e}")
        return {'display_time': "Invalid Date", 'status': "n_a"}

# --- Search and Sort Logic ---
def core_search_links(all_links, search_term, search_type="basic", criteria=None):
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
    sorted_list = list(links_to_sort) 
    if sort_by:
        reverse = (sort_order == 'desc')
        if sort_by == 'title': 
            sorted_list.sort(key=lambda x: x.get('title','').lower(), reverse=reverse)
        elif sort_by == 'created': 
            sorted_list.sort(key=lambda x: x.get('created_timestamp',0), reverse=reverse)
        elif sort_by == 'last_visited': 
            sorted_list.sort(key=lambda x: x.get('last_visited_timestamp',0), reverse=reverse)
        elif sort_by == 'visit_count': 
            sorted_list.sort(key=lambda x: x.get('visit_count',0), reverse=reverse)
        elif sort_by == 'reminder_time': 
            # When sorting by reminder_time (ascending):
            # - Active reminders (non-zero timestamp) come first, sorted by soonest.
            # - Links with no reminder (timestamp 0) go to the end.
            # When sorting descending:
            # - Active reminders come first, sorted by latest.
            # - Links with no reminder (timestamp 0) go to the end (or beginning if preferred by reversing tuple).
            # This key puts 0s (no reminder) last for ascending, first for descending due to natural tuple sort.
            if not reverse: # Ascending: soonest actual reminders first, then 0s (no reminder)
                sorted_list.sort(key=lambda x: (x.get('reminder_timestamp', 0) == 0, x.get('reminder_timestamp', 0)))
            else: # Descending: latest actual reminders first, then 0s (no reminder)
                 # To make 0s appear last in descending as well:
                 # sorted_list.sort(key=lambda x: (x.get('reminder_timestamp', 0) != 0, x.get('reminder_timestamp', 0)), reverse=True)
                 # Simpler: just reverse the ascending logic for 0s
                 sorted_list.sort(key=lambda x: (x.get('reminder_timestamp', 0) == 0, x.get('reminder_timestamp', 0)), reverse=True)
                 # This will put 0s (is_zero=True) first, then non-zeros (is_zero=False) which is what we want for descending if 0s are "least important".
                 # If you want 0s last in descending order as well, the key needs to be more complex,
                 # e.g., assign a very large number to 0 timestamps for descending or very small for ascending.
                 # Let's stick to: Ascending = active reminders soonest, then no reminders.
                 # Descending = no reminders first, then active reminders latest.
                 # A simpler way for descending that puts 0s last:
                 sorted_list.sort(key=lambda x: x.get('reminder_timestamp', float('-inf') if reverse else float('inf')), reverse=reverse)


    return sorted_list

# Load config when this module is imported
load_config()

