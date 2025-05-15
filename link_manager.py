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
        # Ensure file is not empty before trying to load
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
        # print("Links saved successfully.") # Optional: can be noisy in CLI
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
    
    # Determine created_timestamp
    created_ts = int(time.time()) # Current time for a new link

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
        return

    print("\n--- Your Links ---")
    for index, link in enumerate(links):
        print(f"{index + 1}. Title: {link.get('title', 'N/A')}")
        print(f"   URL: {link.get('url', 'N/A')}")
        print(f"   ID: {link.get('id', 'N/A')}") # Useful for future delete/edit
        print("-" * 10)
    print("------------------\n")

def main_cli():
    """Main function to run the command-line interface."""
    while True:
        print("\nInteractive Link Manager")
        print("1. Add Link")
        print("2. View Links")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ").strip()

        if choice == '1':
            add_link_interactive()
        elif choice == '2':
            view_links_interactive()
        elif choice == '3':
            print("Exiting Link Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 3.")

if __name__ == "__main__":
    # Ensure DATA_FILE exists, create if not (to prevent error on first getctime if we were using it)
    # For now, load_links() handles non-existence gracefully.
    # if not os.path.exists(DATA_FILE):
    #    save_links([]) # Create an empty list file if it doesn't exist

    main_cli()

