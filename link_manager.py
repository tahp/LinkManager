import json
import os
import uuid # For unique link IDs later
import time
from datetime import datetime # For formatting timestamp and parsing reminder input
# import shlex # Kept for potential future use

# Define the name of our data files
DATA_FILE = "links.json"
CONFIG_FILE = "config.json"

# Global variable to hold loaded configuration
CONFIG = {}

# --- Configuration Functions ---
def load_config():
    """Loads configuration from config.json, or returns defaults."""
    global CONFIG
    defaults = {
        "page_size": 5,
        "date_format_choice": "1", # Corresponds to '%Y-%m-%d %H:%M:%S'
        "date_formats": {
            "1": "%Y-%m-%d %H:%M:%S", # Default
            "2": "%d/%m/%Y %H:%M",   # Day/Month/Year Hour:Minute
            "3": "%m/%d/%y %I:%M %p"    # Month/Day/YearShort Hour(12):Minute AM/PM
        },
        "default_export_path": "~/" # Default to home directory
    }
    if not os.path.exists(CONFIG_FILE):
        CONFIG = defaults
        save_config() # Save defaults if no config file exists
        return

    try:
        with open(CONFIG_FILE, 'r') as f:
            loaded_config = json.load(f)
            # Ensure all keys from defaults are present
            for key, value in defaults.items():
                loaded_config.setdefault(key, value)
            # Special handling for date_formats if user manually edited config
            if not isinstance(loaded_config.get("date_formats"), dict) or \
               not all(k in loaded_config["date_formats"] for k in ["1","2","3"]):
                loaded_config["date_formats"] = defaults["date_formats"]

            CONFIG = loaded_config
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading config: {e}. Using default settings.")
        CONFIG = defaults
    except Exception as e:
        print(f"Unexpected error loading config: {e}. Using default settings.")
        CONFIG = defaults

def save_config():
    """Saves the current CONFIG to config.json."""
    global CONFIG
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(CONFIG, f, indent=4)
        # print("Configuration saved.") # Optional feedback
        return True
    except IOError as e:
        print(f"Error saving configuration: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error saving configuration: {e}")
        return False

def get_active_date_format_str():
    """Gets the strftime format string based on current config."""
    global CONFIG
    choice = CONFIG.get("date_format_choice", "1")
    return CONFIG.get("date_formats", {}).get(choice, "%Y-%m-%d %H:%M:%S") # Default to ISO like if error

# --- Modified existing functions to use CONFIG ---
def format_timestamp(ts):
    """Formats a Unix timestamp into a human-readable string using configured format."""
    if not ts or ts == 0: return "N/A"
    date_format_str = get_active_date_format_str()
    try:
        return datetime.fromtimestamp(ts).strftime(date_format_str)
    except ValueError: return "Invalid Date"
    except OSError: return "Date out of range"

# load_links and save_links for DATA_FILE remain largely the same,
# but export/import will use config for default export path.

# --- display_links needs to use CONFIG['page_size'] ---
def display_links(links_to_show, sort_by=None, sort_order='asc', title_prefix="--- Links ---", 
                  paginate=False): # Removed page_size from args, will use CONFIG
    global CONFIG
    page_size = CONFIG.get("page_size", 5) # Use configured page size

    # ... (rest of display_links logic from previous step, ensuring it uses the local page_size) ...
    if not links_to_show:
        print(f"\n{title_prefix.replace('---', '--- No')} to display ---")
        return False
    links_to_sort = list(links_to_show)
    if sort_by:
        reverse_order = (sort_order == 'desc')
        if sort_by == 'title': links_to_sort.sort(key=lambda x: x.get('title', '').lower(), reverse=reverse_order)
        elif sort_by == 'created': links_to_sort.sort(key=lambda x: x.get('created_timestamp', 0), reverse=reverse_order)
        # ... other sort keys ...
        elif sort_by == 'last_visited': links_to_sort.sort(key=lambda x: x.get('last_visited_timestamp', 0), reverse=reverse_order)
        elif sort_by == 'visit_count': links_to_sort.sort(key=lambda x: x.get('visit_count', 0), reverse=reverse_order)
        elif sort_by == 'reminder_time': links_to_sort.sort(key=lambda x: x.get('reminder_timestamp', 0), reverse=reverse_order)

    total_items = len(links_to_sort)
    if not paginate or total_items <= page_size:
        header_note = f"(Showing all {total_items} items)" if paginate else "" # only show if paginate was true
        print(f"\n{title_prefix} {header_note}")
        for index, link in enumerate(links_to_sort):
            default_marker = "[Default]" if link.get('is_default') else ""
            print(f"{index + 1}. Title: {link.get('title', 'N/A')} {default_marker}")
            print(f"   URL: {link.get('url', 'N/A')}")
            if link.get('notes'): print(f"   Notes: {link.get('notes')}")
            print(f"   Visits: {link.get('visit_count', 0)}")
            print(f"   Last Visited: {format_timestamp(link.get('last_visited_timestamp', 0))}")
            print(f"   Added: {format_timestamp(link.get('created_timestamp', 0))}")
            print(f"   Reminder: {format_timestamp(link.get('reminder_timestamp', 0))}")
            print(f"   ID: {link.get('id', 'N/A')}")
            print("-" * 10)
        print("-------------")
        return True

    total_pages = (total_items + page_size - 1) // page_size
    current_page = 1
    while True:
        start_index = (current_page - 1) * page_size
        end_index = start_index + page_size
        page_items = links_to_sort[start_index:end_index]
        print(f"\n{title_prefix} (Page {current_page}/{total_pages}, Items {start_index + 1}-{min(end_index, total_items)} of {total_items})")
        for index, link in enumerate(page_items):
            default_marker = "[Default]" if link.get('is_default') else ""
            print(f"{index + 1}. Title: {link.get('title', 'N/A')} {default_marker}")
            # ... print other link details ...
            print(f"   URL: {link.get('url', 'N/A')}")
            if link.get('notes'): print(f"   Notes: {link.get('notes')}")
            print(f"   Visits: {link.get('visit_count', 0)}")
            print(f"   Last Visited: {format_timestamp(link.get('last_visited_timestamp', 0))}")
            print(f"   Added: {format_timestamp(link.get('created_timestamp', 0))}")
            print(f"   Reminder: {format_timestamp(link.get('reminder_timestamp', 0))}")
            print(f"   ID: {link.get('id', 'N/A')}")
            print("-" * 10)
        print("-------------")
        if total_pages <= 1: break
        prompt_str = "Options: Next (n), Prev (p), Go (gX), Quit view (q): "
        page_choice = input(prompt_str).strip().lower()
        if page_choice == 'n':
            if current_page < total_pages: current_page += 1
            else: print("Already on the last page.")
        elif page_choice == 'p':
            if current_page > 1: current_page -= 1
            else: print("Already on the first page.")
        elif page_choice.startswith('g'):
            try:
                target_page_str = page_choice[1:]
                if not target_page_str: raise ValueError("No page number.")
                target_page = int(target_page_str)
                if 1 <= target_page <= total_pages: current_page = target_page
                else: print(f"Page number out of range (1-{total_pages}).")
            except ValueError: print("Invalid 'go to page' format (e.g., g3).")
        elif page_choice == 'q': break
        else: print("Invalid option.")
    return True

# view_all_links_interactive, search_links_interactive, view_reminders_interactive
# will call display_links with paginate=True, and display_links will pick up page_size from CONFIG.

def view_all_links_interactive():
    all_links = load_links()
    title_prefix="--- All Links ---"
    if not all_links: display_links(all_links, title_prefix=title_prefix); return
    sort_by, sort_order = get_sort_preferences()
    display_links(all_links, sort_by=sort_by, sort_order=sort_order, 
                  title_prefix=title_prefix, paginate=True) # paginate=True

def basic_search_links_interactive():
    # ... (search logic) ...
    # When displaying:
    # display_links(filtered_links, ..., paginate=True)
    print("\n--- Basic Search Links ---")
    search_term = input("Enter search term: ").strip().lower()
    if not search_term: print("Search term empty."); return
    all_links = load_links(); filtered_links = []
    if not all_links: print("No links to search."); return
    for link in all_links:
        if search_term in link.get('title', '').lower() or \
           search_term in link.get('url', '').lower() or \
           search_term in link.get('notes', '').lower():
            filtered_links.append(link)
    if not filtered_links: print(f"No links found for '{search_term}'.")
    else:
        print(f"\nFound {len(filtered_links)} link(s) for '{search_term}':")
        sort_by, sort_order = get_sort_preferences()
        display_links(filtered_links, sort_by=sort_by, sort_order=sort_order, 
                      title_prefix=f"--- Search Results for '{search_term}' ---", paginate=True)
    print("--------------------")


def advanced_search_links_interactive():
    # ... (search logic) ...
    # When displaying:
    # display_links(filtered_links, ..., paginate=True)
    print("\n--- Advanced Search Links ---")
    print("Syntax: field:value (e.g., title:work notes:important is:default)")
    query_str = input("Enter advanced search query: ").strip().lower()
    if not query_str: print("Query empty."); return
    all_links = load_links(); filtered_links = []
    if not all_links: print("No links to search."); return
    criteria_parts = query_str.split(); parsed_criteria = []; valid_query = True
    for part in criteria_parts:
        if ':' not in part: print(f"Invalid: '{part}'. Expected 'field:value'."); valid_query = False; break
        field, value = part.split(':', 1)
        if field not in ['title', 'url', 'notes', 'is']: print(f"Invalid field: '{field}'."); valid_query = False; break
        if field == 'is' and value not in ['default', 'not-default']: print(f"Invalid value for 'is': '{value}'."); valid_query = False; break
        parsed_criteria.append({'field': field, 'value': value})
    if not valid_query or not parsed_criteria: return
    for link in all_links: # Corrected variable name
        match_all = True
        for crit in parsed_criteria:
            f, v = crit['field'], crit['value']
            if f == 'title' and v not in link.get('title','').lower(): match_all=False; break
            elif f == 'url' and v not in link.get('url','').lower(): match_all=False; break
            elif f == 'notes' and v not in link.get('notes','').lower(): match_all=False; break
            elif f == 'is':
                if v == 'default' and not link.get('is_default'): match_all=False; break
                if v == 'not-default' and link.get('is_default'): match_all=False; break
        if match_all: filtered_links.append(link) # Corrected variable name
    if not filtered_links: print(f"No links found for '{query_str}'.")
    else:
        print(f"\nFound {len(filtered_links)} link(s) for '{query_str}':")
        sort_by, sort_order = get_sort_preferences()
        display_links(filtered_links, sort_by=sort_by, sort_order=sort_order, 
                      title_prefix=f"--- Advanced Search Results ---", paginate=True)
    print("---------------------------")

def view_reminders_interactive():
    # ... (reminder logic) ...
    # When displaying:
    # display_links(due_overdue_reminders, ..., paginate=True)
    # display_links(upcoming_reminders, ..., paginate=True)
    print("\n--- View Reminders ---")
    all_links = load_links(); now_ts = int(time.time()); due = []; upcoming = []
    if not all_links: print("No links for reminders."); return
    for link in all_links:
        rem_ts = link.get('reminder_timestamp', 0)
        if rem_ts > 0:
            if rem_ts <= now_ts: due.append(link)
            else: upcoming.append(link)
    rem_found = False
    if due:
        rem_found = True
        display_links(due, sort_by='reminder_time', sort_order='asc', 
                      title_prefix="--- Due/Overdue Reminders ---", paginate=True)
    else: print("\nNo due or overdue reminders.")
    if upcoming:
        rem_found = True
        display_links(upcoming, sort_by='reminder_time', sort_order='asc', 
                      title_prefix="--- Upcoming Reminders ---", paginate=True)
    else: print("\nNo upcoming reminders.")
    if not rem_found : print("\nNo reminders are currently set or active.")
    print("----------------------")


def export_links_interactive():
    global CONFIG
    print("\n--- Export Links ---")
    current_links = load_links()
    if not current_links and input("No links. Create empty export? (y/n): ").lower() != 'y': return

    # Use configured default path, then timestamped filename
    default_export_dir = os.path.expanduser(CONFIG.get("default_export_path", "~/"))
    if not default_export_dir.endswith('/'): default_export_dir += '/'
    default_filename = f"links_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    suggested_path = os.path.join(default_export_dir, default_filename) # Use os.path.join

    print(f"\nTip: To save to shared storage, ensure 'termux-setup-storage' has been run.")
    print(f"Default export directory is: {default_export_dir}")
    export_filepath_str = input(f"Enter filename or full path for export (default: {suggested_path}): ").strip()
    
    export_filepath = os.path.expanduser(export_filepath_str or suggested_path)

    try:
        export_dir_actual = os.path.dirname(export_filepath)
        if export_dir_actual and not os.path.exists(export_dir_actual):
            os.makedirs(export_dir_actual); print(f"Created directory: {export_dir_actual}")
    except OSError as e: print(f"Error creating directory: {e}"); return
    except Exception as e: print(f"Invalid path: {e}"); return

    if save_links(current_links, export_filepath): print(f"Exported {len(current_links)} links to: {export_filepath}")
    else: print(f"Failed to export to: {export_filepath}")
    print("--------------------")

# --- New Settings Function ---
def configure_settings_interactive():
    """Allows user to configure application settings."""
    global CONFIG
    print("\n--- Configure Settings ---")
    
    while True:
        print("\nCurrent Settings:")
        print(f"1. Page Size for lists: {CONFIG.get('page_size', 5)}")
        
        current_format_choice = CONFIG.get('date_format_choice', "1")
        current_format_str = CONFIG.get('date_formats', {}).get(current_format_choice, "N/A")
        print(f"2. Date Display Format: Choice {current_format_choice} ({current_format_str})")
        
        print(f"3. Default Export Path: {CONFIG.get('default_export_path', '~/')}")
        print("0. Back to Main Menu")

        choice = input("Enter setting to change (0-3): ").strip()

        if choice == '0':
            break
        elif choice == '1':
            try:
                new_size_str = input(f"Enter new page size (current: {CONFIG.get('page_size')}): ").strip()
                if new_size_str: # Only update if user entered something
                    new_size = int(new_size_str)
                    if new_size > 0:
                        CONFIG['page_size'] = new_size
                        print(f"Page size set to {new_size}.")
                    else:
                        print("Page size must be a positive number.")
            except ValueError:
                print("Invalid input. Page size must be a number.")
        elif choice == '2':
            print("Available Date Formats:")
            for k, v_format in CONFIG.get("date_formats", {}).items():
                # Show example using current time
                example_time = datetime.now().strftime(v_format)
                print(f"  {k}: {v_format} (e.g., {example_time})")
            
            new_format_choice = input("Enter choice for date format: ").strip()
            if new_format_choice in CONFIG.get("date_formats", {}):
                CONFIG['date_format_choice'] = new_format_choice
                print(f"Date format set to choice {new_format_choice}.")
            else:
                print("Invalid choice for date format.")
        elif choice == '3':
            new_path = input(f"Enter new default export path (current: {CONFIG.get('default_export_path')}): ").strip()
            if new_path: # Only update if user entered something
                # Basic validation: should probably check if it's a writable dir, but keep it simple for now
                CONFIG['default_export_path'] = new_path
                print(f"Default export path set to {new_path}.")
        else:
            print("Invalid choice.")

        save_config() # Save after each change or at the end of the loop
    print("------------------------")


# --- Main CLI ---
def main_cli():
    global CONFIG
    load_config() # Load configuration at the start

    while True:
        print("\nInteractive Link Manager")
        # ... (menu options 1-8 remain the same) ...
        print("1. Add Link")
        print("2. View All Links")
        print("3. Delete Link")
        print("4. Edit Link")
        print("5. Visit Link")
        print("6. Basic Search Links")
        print("7. Advanced Search Links")
        print("8. View Reminders")
        print("9. Export Links")
        print("10. Import Links")
        print("11. Settings")         # New
        print("12. Exit")            # Shifted
        choice = input("Enter your choice (1-12): ").strip()

        if choice == '1': add_link_interactive()
        elif choice == '2': view_all_links_interactive()
        # ... (elif for 3-8) ...
        elif choice == '3': delete_link_interactive()
        elif choice == '4': edit_link_interactive()
        elif choice == '5': visit_link_interactive()
        elif choice == '6': basic_search_links_interactive()
        elif choice == '7': advanced_search_links_interactive()
        elif choice == '8': view_reminders_interactive()
        elif choice == '9': export_links_interactive()
        elif choice == '10': import_links_interactive()
        elif choice == '11': configure_settings_interactive() # New
        elif choice == '12':
            print("Exiting Link Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 12.")

# Ensure all other functions (prompt_for_reminder_datetime, add_link_interactive, get_sort_preferences,
# view_all_links_interactive, delete_link_interactive, edit_link_interactive, visit_link_interactive,
# basic_search_links_interactive, advanced_search_links_interactive, view_reminders_interactive,
# export_links_interactive, import_links_interactive) are correctly defined in your full script.
# I've included stubs or full versions for modified ones.

if __name__ == "__main__":
    main_cli()
