import json
import os
import uuid # For unique link IDs later
import time

# Define the name of our data file
DATA_FILE = "links.json"

def load_links():
    """Loads links from the JSON data file."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        if os.path.getsize(DATA_FILE) == 0:
            return []
        with open(DATA_FILE, 'r') as f:
            links = json.load(f)
            return links
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
    
    links = load_links()
    created_ts = int(time.time())

    new_link = {
        "id": str(uuid.uuid4()),
        "url": url,
        "title": title if title else url,
        "is_default": False,
        "reminder_timestamp": 0,
        "last_visited_timestamp": 0,
        "visit_count": 0,
        "notes": "",
        "created_timestamp": created_ts
    }
    
    links.append(new_link)
    save_links(links)
    print(f"Link added: {new_link['title']}")
    print("--------------------")

def view_links_interactive():
    """Displays all current links with index numbers."""
    links = load_links()
    if not links:
        print("\nNo links to display.")
        return False # Indicate that no links were displayed

    print("\n--- Your Links ---")
    for index, link in enumerate(links):
        print(f"{index + 1}. Title: {link.get('title', 'N/A')}")
        print(f"   URL: {link.get('url', 'N/A')}")
        print(f"   ID: {link.get('id', 'N/A')}")
        print("-" * 10)
    print("------------------\n")
    return True # Indicate that links were displayed

def delete_link_interactive():
    """Handles deleting an existing link via user input."""
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
        
        confirm = input(f"Are you sure you want to delete '{link_to_delete.get('title', 'N/A')}'? (y/n): ").strip().lower()
        
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
    """Handles editing an existing link via user input."""
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

        link_to_edit_index = choice - 1 # Adjust for 0-based index
        link_to_edit = links[link_to_edit_index]

        print(f"\nEditing link: '{link_to_edit.get('title', 'N/A')}'")
        print(f"Current URL: {link_to_edit.get('url')}")
        new_url = input(f"Enter new URL (or press Enter to keep current): ").strip()
        if new_url and not (new_url.startswith("http://") or new_url.startswith("https://")):
            print("Invalid URL format. Must start with http:// or https://. URL not changed.")
            new_url = link_to_edit.get('url') # Keep old URL
        elif not new_url:
            new_url = link_to_edit.get('url') # Keep old URL if input is empty

        print(f"Current Title: {link_to_edit.get('title')}")
        new_title = input(f"Enter new title (or press Enter to keep current): ").strip()
        if not new_title:
            new_title = link_to_edit.get('title') # Keep old title if input is empty
        elif not title and new_url: # If title becomes empty but new_url is not, default title to new_url
             new_title = new_url


        # Update the link in the list
        links[link_to_edit_index]['url'] = new_url
        links[link_to_edit_index]['title'] = new_title if new_title else new_url # Ensure title is not empty if URL exists
        # We could also update a 'modified_timestamp' here if we add one to the link structure

        save_links(links)
        print(f"Link updated successfully to: '{links[link_to_edit_index]['title']}'")

    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"An unexpected error occurred during edit: {e}")
    print("-----------------")


def main_cli():
    """Main function to run the command-line interface."""
    while True:
        print("\nInteractive Link Manager")
        print("1. Add Link")
        print("2. View Links")
        print("3. Delete Link")
        print("4. Edit Link")   # New option
        print("5. Exit")        # Exit is now 5
        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            add_link_interactive()
        elif choice == '2':
            view_links_interactive()
        elif choice == '3':
            delete_link_interactive()
        elif choice == '4': # New branch for edit
            edit_link_interactive()
        elif choice == '5': # Exit condition updated
            print("Exiting Link Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main_cli()
