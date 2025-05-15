import json
import os
import uuid # For unique link IDs later
import time
from datetime import datetime # For formatting timestamp

# Define the name of our data file
DATA_FILE = "links.json"

def format_timestamp(ts):
    """Formats a Unix timestamp into a human-readable string."""
    if not ts or ts == 0:
        return "N/A"
    try:
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return "Invalid Date"

def load_links():
    """Loads links from the JSON data file."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        if os.path.getsize(DATA_FILE) == 0:
            return []
        with open(DATA_FILE, 'r') as f:
            links_data = json.load(f)
            # Ensure all links have new fields, providing defaults if missing
            for link in links_data:
                link.setdefault('notes', '')
                link.setdefault('is_default', False)
                link.setdefault('url', '')
                link.setdefault('title', link.get('url', 'N/A'))
                link.setdefault('id', str(uuid.uuid4()))
                link.setdefault('reminder_timestamp', 0)
                link.setdefault('last_visited_timestamp', 0) # Ensure this exists
                link.setdefault('visit_count', 0)            # Ensure this exists
                link.setdefault('created_timestamp', int(time.time()))
            return links_data
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading links: {e}")
        return []

def save_links(links):
    """Saves the list of links to the JSON data file."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(links, f, indent=4)
    except IOError as e:
        print(f"Error saving links: {e}")

def add_link_interactive():
    """Handles adding a new link via user input."""
    print("\n--- Add New Link ---")
    url = input("Enter the URL (must start with http:// or https://): ").strip()
    if not url:
        print("URL cannot be empty. Link not added.")
        return
    if not (url.startswith("http://") or url.startswith("https://")):
        print("Invalid URL format. Must start with http:// or https://. Link not added.")
        return

    title = input("Enter a title (optional, press Enter to use URL as title): ").strip()
    notes = input("Enter notes (optional): ").strip()
    is_default_input = input("Mark as default link? (y/n, default n): ").strip().lower()
    is_default = True if is_default_input == 'y' else False
    
    links = load_links()
    created_ts = int(time.time())

    new_link = {
        "id": str(uuid.uuid4()),
        "url": url,
        "title": title if title else url,
        "notes": notes,
        "is_default": is_default,
        "reminder_timestamp": 0,
        "last_visited_timestamp": 0, # Initialized to 0
        "visit_count": 0,            # Initialized to 0
        "created_timestamp": created_ts
    }
    
    links.append(new_link)
    save_links(links)
    print(f"Link added: {new_link['title']}")
    print("--------------------")

def view_links_interactive():
    """Displays all current links with index numbers and new fields."""
    links = load_links()
    if not links:
        print("\nNo links to display.")
        return False

    print("\n--- Your Links ---")
    for index, link in enumerate(links):
        default_marker = "[Default]" if link.get('is_default') else ""
        print(f"{index + 1}. Title: {link.get('title', 'N/A')} {default_marker}")
        print(f"   URL: {link.get('url', 'N/A')}")
        if link.get('notes'):
            print(f"   Notes: {link.get('notes')}")
        print(f"   Visits: {link.get('visit_count', 0)}")
        print(f"   Last Visited: {format_timestamp(link.get('last_visited_timestamp', 0))}")
        print(f"   ID: {link.get('id', 'N/A')}")
        print("-" * 10)
    print("------------------\n")
    return True

def delete_link_interactive():
    # ... (keep existing delete_link_interactive function as is) ...
    print("\n--- Delete Link ---")
    if not view_links_interactive():
        return

    links = load_links()
    if not links:
        print("No links available to delete.") # Should be caught by view_links_interactive
        return

    try:
        choice_str = input("Enter the number of the link to delete: ").strip()
        if not choice_str:
            print("No selection made. Deletion cancelled.")
            return
            
        choice = int(choice_str)
        
        if choice < 1 or choice > len(links):
            print("Invalid link number. Please try again.")
            return

        link_to_delete = links[choice - 1]
        
        default_warning = " This is a default link." if link_to_delete.get('is_default') else ""
        confirm = input(f"Are you sure you want to delete '{link_to_delete.get('title', 'N/A')}'?{default_warning} (y/n): ").strip().lower()
        
        if confirm == 'y':
            deleted_link = links.pop(choice - 1)
            save_links(links)
            print(f"Link '{deleted_link.get('title', 'N/A')}' deleted successfully.")
        else:
            print("Deletion cancelled.")
            
    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    print("-------------------")


def edit_link_interactive():
    # ... (keep existing edit_link_interactive function as is) ...
    print("\n--- Edit Link ---")
    if not view_links_interactive(): # Display links first
        return

    links = load_links()
    if not links: # Should be caught by view_links_interactive
        print("No links available to edit.")
        return

    try:
        choice_str = input("Enter the number of the link to edit: ").strip()
        if not choice_str:
            print("No selection made. Edit cancelled.")
            return

        choice = int(choice_str)

        if choice < 1 or choice > len(links):
            print("Invalid link number. Please try again.")
            return

        link_to_edit_index = choice - 1
        link_to_edit = links[link_to_edit_index]

        print(f"\nEditing link: '{link_to_edit.get('title', 'N/A')}'")
        
        # Edit URL
        print(f"Current URL: {link_to_edit.get('url')}")
        new_url = input(f"Enter new URL (or press Enter to keep current): ").strip()
        if new_url and not (new_url.startswith("http://") or new_url.startswith("https://")):
            print("Invalid URL format. URL not changed.")
            new_url = link_to_edit.get('url')
        elif not new_url:
            new_url = link_to_edit.get('url')

        # Edit Title
        print(f"Current Title: {link_to_edit.get('title')}")
        new_title = input(f"Enter new title (or press Enter to keep current): ").strip()
        if not new_title:
            new_title = link_to_edit.get('title')
        
        # Edit Notes
        print(f"Current Notes: {link_to_edit.get('notes', '')}") 
        new_notes_input = input("Enter new notes (or press Enter to keep current, type 'clear' to remove notes): ").strip()
        if new_notes_input.lower() == 'clear':
            new_notes = ''
        elif new_notes_input: # If user typed something (and it wasn't 'clear')
            new_notes = new_notes_input
        else: # User pressed enter
            new_notes = link_to_edit.get('notes', '')


        # Edit Default Status
        current_default_status = "y" if link_to_edit.get('is_default') else "n"
        print(f"Currently a default link: {current_default_status.upper()}")
        is_default_input = input(f"Make this a default link? (y/n, Enter to keep '{current_default_status}'): ").strip().lower()
        new_is_default = link_to_edit.get('is_default') 
        if is_default_input == 'y':
            new_is_default = True
        elif is_default_input == 'n':
            new_is_default = False

        links[link_to_edit_index]['url'] = new_url
        links[link_to_edit_index]['title'] = new_title if new_title else new_url
        links[link_to_edit_index]['notes'] = new_notes
        links[link_to_edit_index]['is_default'] = new_is_default
        
        save_links(links)
        print(f"Link updated successfully: '{links[link_to_edit_index]['title']}'")

    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"An unexpected error occurred during edit: {e}")
    print("-----------------")

def visit_link_interactive():
    """Handles 'visiting' a link: updates visit count and timestamp."""
    print("\n--- Visit Link ---")
    if not view_links_interactive(): # Display links first
        return

    links = load_links()
    if not links: # Should be caught by view_links_interactive
        print("No links available to visit.")
        return

    try:
        choice_str = input("Enter the number of the link to mark as visited: ").strip()
        if not choice_str:
            print("No selection made. Visit cancelled.")
            return
            
        choice = int(choice_str)

        if choice < 1 or choice > len(links):
            print("Invalid link number. Please try again.")
            return

        link_to_visit_index = choice - 1
        
        # Update visit count and timestamp
        links[link_to_visit_index]['visit_count'] = links[link_to_visit_index].get('visit_count', 0) + 1
        links[link_to_visit_index]['last_visited_timestamp'] = int(time.time())
        
        save_links(links)
        
        visited_link_title = links[link_to_visit_index].get('title', 'N/A')
        visited_link_url = links[link_to_visit_index].get('url', 'N/A')
        print(f"Marked '{visited_link_title}' as visited.")
        print(f"URL: {visited_link_url}") # Display URL as a pseudo-action
        
    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    print("------------------")


def main_cli():
    """Main function to run the command-line interface."""
    while True:
        print("\nInteractive Link Manager")
        print("1. Add Link")
        print("2. View Links")
        print("3. Delete Link")
        print("4. Edit Link")
        print("5. Visit Link")   # New option
        print("6. Exit")        # Exit is now 6
        choice = input("Enter your choice (1-6): ").strip()

        if choice == '1':
            add_link_interactive()
        elif choice == '2':
            view_links_interactive()
        elif choice == '3':
            delete_link_interactive()
        elif choice == '4':
            edit_link_interactive()
        elif choice == '5': # New branch for visit
            visit_link_interactive()
        elif choice == '6': # Exit condition updated
            print("Exiting Link Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main_cli()
