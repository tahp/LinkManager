import json
import os
import uuid # For unique link IDs later
import time
# Define the name of our data file
DATA_FILE = "links.json"

def load_links():
    """Loads links from the JSON data file."""
    if not os.path.exists(DATA_FILE):
        return [] # Return an empty list if the file doesn't exist
    try:
        with open(DATA_FILE, 'r') as f:
            links = json.load(f)
            return links
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading links: {e}")
        return [] # Return empty list on error

def save_links(links):
    """Saves the list of links to the JSON data file."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(links, f, indent=4) # indent for pretty printing
        print("Links saved successfully.")
    except IOError as e:
        print(f"Error saving links: {e}")

def add_link(url, title=""):
    """Adds a new link to our list."""
    links = load_links()
    
    if not url.startswith("http://") and not url.startswith("https://"):
        print("Error: URL must start with http:// or https://")
        return

    # Basic structure for a link - we will expand this
    new_link = {
        "id": str(uuid.uuid4()), # Generate a unique ID
        "url": url,
        "title": title if title else url, # Use URL as title if not provided
        "is_default": False,
        "reminder_timestamp": 0,
        "last_visited_timestamp": 0,
        "visit_count": 0,
        "notes": "",
        "created_timestamp": int(os.path.getctime(DATA_FILE)) if os.path.exists(DATA_FILE) else int(time.time()) # Placeholder for now
    }
    
    links.append(new_link)
    save_links(links)
    print(f"Link added: {new_link['title']}")

def view_links():
    """Displays all current links."""
    links = load_links()
    if not links:
        print("No links to display.")
        return

    print("\n--- Your Links ---")
    for index, link in enumerate(links):
        print(f"{index + 1}. Title: {link.get('title', 'N/A')}")
        print(f"   URL: {link.get('url', 'N/A')}")
        print(f"   ID: {link.get('id', 'N/A')}") # Useful for future delete/edit
        print("-" * 10)
    print("------------------\n")

# --- Main execution for simple testing ---
if __name__ == "__main__":
    # Example Usage (we'll build a proper CLI later)
    
    # Clear the file for fresh testing (optional)
    # if os.path.exists(DATA_FILE):
    #     os.remove(DATA_FILE)

    print("Interactive Link Manager - Basic Test")
    
    # Add a few sample links
    add_link("https://www.google.com", "Google Search")
    add_link("https://www.github.com", "GitHub")
    
    # View all links
    view_links()
    
    # Example of adding a link without a specific title
    add_link("https://news.ycombinator.com")
    view_links()
