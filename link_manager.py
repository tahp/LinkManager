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
    except ValueError: # Handles potential errors if ts is out of range for fromtimestamp
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
            for link in links_data:
                link.setdefault('notes', '')
                link.setdefault('is_default', False)
                link.setdefault('url', '')
                link.setdefault('title', link.get('url', 'N/A'))
                link.setdefault('id', str(uuid.uuid4()))
                link.setdefault('reminder_timestamp', 0)
                link.setdefault('last_visited_timestamp', 0)
                link.setdefault('visit_count', 0)
                link.setdefault('created_timestamp', int(time.time())) # Default to current if missing
            return links_data
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading links: {e}")
        return []

def save_links(links):
    # ... (keep existing save_links function as is) ...
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(links, f, indent=4)
    except IOError as e:
        print(f"Error saving links: {e}")


def add_link_interactive():
    # ... (keep existing add_link_interactive function as is) ...
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
    # Use current time for created_timestamp when adding a new link
    created_ts = int(time.time()) 

    new_link = {
        "id": str(uuid.uuid4()),
        "url": url,
        "title": title if title else url,
        "notes": notes,
        "is_default": is_default,
        "reminder_timestamp": 0,
        "last_visited_timestamp": 0,
        "visit_count": 0,
        "created_timestamp": created_ts # Set at creation
    }
    
    links.append(new_link)
    save_links(links)
    print(f"Link added: {new_link['title']}")
    print("--------------------")


def display_links(links_to_show, sort_by=None, sort_order='asc'):
    """Displays a given list of links, with optional sorting."""
    if not links_to_show:
        print("\nNo links to display.")
        return False

    # Create a copy to sort, to avoid modifying the original list if passed by reference
    links_to_sort = list(links_to_show)

    if sort_by:
        reverse_order = (sort_order == 'desc')
        if sort_by == 'title':
            links_to_sort.sort(key=lambda x: x.get('title', '').lower(), reverse=reverse_order)
        elif sort_by == 'created': # Sort by 'created_timestamp'
            links_to_sort.sort(key=lambda x: x.get('created_timestamp', 0), reverse=reverse_order)
        elif sort_by == 'last_visited':
            links_to_sort.sort(key=lambda x: x.get('last_visited_timestamp', 0), reverse=reverse_order)
        elif sort_by == 'visit_count':
            links_to_sort.sort(key=lambda x: x.get('visit_count', 0), reverse=reverse_order)
    
    # If no sort_by is provided, links_to_sort remains in its original order (or order from load_links)

    print("\n--- Links ---")
    for index, link in enumerate(links_to_sort): # Iterate over the (potentially) sorted list
        default_marker = "[Default]" if link.get('is_default') else ""
        print(f"{index + 1}. Title: {link.get('title', 'N/A')} {default_marker}")
        print(f"   URL: {link.get('url', 'N/A')}")
        if link.get('notes'):
            print(f"   Notes: {link.get('notes')}")
        print(f"   Visits: {link.get('visit_count', 0)}")
        print(f"   Last Visited: {format_timestamp(link.get('last_visited_timestamp', 0))}")
        print(f"   Added: {format_timestamp(link.get('created_timestamp', 0))}") # Display created_timestamp
        print(f"   ID: {link.get('id', 'N/A')}")
        print("-" * 10)
    print("-------------")
    return True

def get_sort_preferences():
    """Prompts user for sort criteria and order."""
    print("\nSort options:")
    print("  Sort by: 1. Title  2. Date Added  3. Last Visited  4. Visit Count  0. No Sort")
    sort_choice = input("  Enter sort field choice (0-4): ").strip()

    sort_by_key = None
    if sort_choice == '1':
        sort_by_key = 'title'
    elif sort_choice == '2':
        sort_by_key = 'created'
    elif sort_choice == '3':
        sort_by_key = 'last_visited'
    elif sort_choice == '4':
        sort_by_key = 'visit_count'
    elif sort_choice == '0':
        return None, None # No sorting
    else:
        print("  Invalid sort field choice. No sorting will be applied.")
        return None, None

    print("  Order: 1. Ascending  2. Descending")
    order_choice = input(f"  Sort '{sort_by_key}' by (1-2, default Ascending): ").strip()
    sort_order_str = 'asc'
    if order_choice == '2':
        sort_order_str = 'desc'
    elif order_choice != '1' and order_choice != '': # if not 1 and not empty
        print("  Invalid order choice. Defaulting to Ascending.")

    return sort_by_key, sort_order_str


def view_all_links_interactive():
    """Loads and displays all links, with optional sorting."""
    all_links = load_links()
    if not all_links:
        display_links(all_links) # This will print "No links to display."
        return

    sort_by, sort_order = get_sort_preferences()
    display_links(all_links, sort_by=sort_by, sort_order=sort_order)


def delete_link_interactive():
    # ... (keep existing delete_link_interactive function as is, 
    # it already calls view_all_links_interactive which will now offer sort) ...
    print("\n--- Delete Link ---")
    view_all_links_interactive() 
    
    links = load_links() 
    if not links: 
        return

    try:
        choice_str = input("Enter the number of the link to delete (as shown in the list): ").strip() # Clarified prompt
        if not choice_str:
            print("No selection made. Deletion cancelled.")
            return
            
        choice = int(choice_str)
        
        # IMPORTANT: The 'choice' here refers to the index in the *potentially sorted* list
        # that was just displayed. We need to map this back to an item in the original `links` list.
        # For simplicity in this CLI, we will re-load and assume the user is careful or
        # we accept that deletion after sorting can be tricky without stable IDs visible or used for selection.
        # A more robust way would be to delete by ID.
        # For now, let's keep it simple: if sorted, the numbers might not map directly to original storage order.
        # One simple fix: load_links() provides the list in a consistent (though not necessarily sorted) order.
        # If we always operate on the `links` list loaded at the start of the function, choice is relative to that.
        # The `view_all_links_interactive()` call is for display only.

        # To make deletion by number safer after sorting, we should ideally ask for ID or re-display a non-sorted list
        # for deletion. Or, the user understands the number pertains to the *just displayed, possibly sorted* list.
        # Let's assume the user uses the number from the list they just saw.
        # We need to ensure the displayed list's numbering corresponds to what we can pop.
        # The easiest way is to sort `links` (the list we operate on) if sort options were chosen for display,
        # or instruct user to delete by ID (future enhancement).
        # For now, the `links` list loaded for deletion is not sorted.
        # The `view_all_links_interactive` is just for visual aid. This means the user must note the ID.

        # A better approach for interactive delete when display can be sorted:
        # 1. Display links (sorted or not). User sees numbers.
        # 2. Ask for number.
        # 3. If display was sorted, we need to find the actual item from the original unsorted list.
        # This is tricky if only relying on list index.
        # Let's adjust: Deletion will use numbers from an unsorted display for safety for now, or prompt by ID.
        # For this iteration, we'll keep it simpler: the view before delete shows numbers.
        # We will re-fetch the list for `links` for the operation, which is unsorted.
        # This means the number they enter should ideally correspond to the original order, not a sorted one,
        # which is confusing.
        #
        # Solution for now: Let `delete_link_interactive` display a fresh, unsorted list to pick from.
        
        temp_links_for_selection = load_links()
        if not temp_links_for_selection:
            print("No links available to delete.")
            return
        
        print("\n--- Select Link to Delete (from list below) ---")
        display_links(temp_links_for_selection) # Display fresh, unsorted list with numbers

        if not temp_links_for_selection: # Should be caught by display_links
             return

        choice_str = input("Enter the number of the link to delete: ").strip()
        if not choice_str:
            print("No selection made. Deletion cancelled.")
            return
        choice = int(choice_str)


        if choice < 1 or choice > len(temp_links_for_selection):
            print("Invalid link number. Please try again.")
            return

        link_to_delete_from_original_list = temp_links_for_selection[choice - 1]
        
        # Now find this link in the main `links` list by ID to ensure we delete the correct one
        actual_links_for_deletion = load_links()
        index_to_delete = -1
        for i, link in enumerate(actual_links_for_deletion):
            if link.get('id') == link_to_delete_from_original_list.get('id'):
                index_to_delete = i
                break
        
        if index_to_delete == -1:
            print("Error: Link not found for deletion. It might have been deleted already.")
            return

        link_to_delete_obj = actual_links_for_deletion[index_to_delete]
        default_warning = " This is a default link." if link_to_delete_obj.get('is_default') else ""
        confirm = input(f"Are you sure you want to delete '{link_to_delete_obj.get('title', 'N/A')}'?{default_warning} (y/n): ").strip().lower()
        
        if confirm == 'y':
            deleted_link_obj = actual_links_for_deletion.pop(index_to_delete)
            save_links(actual_links_for_deletion)
            print(f"Link '{deleted_link_obj.get('title', 'N/A')}' deleted successfully.")
        else:
            print("Deletion cancelled.")
            
    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    print("-------------------")


def edit_link_interactive():
    # Similar logic to delete for selecting the correct link if display was sorted
    print("\n--- Edit Link ---")
    temp_links_for_selection = load_links()
    if not temp_links_for_selection:
        print("No links available to edit.")
        return
        
    print("\n--- Select Link to Edit (from list below) ---")
    display_links(temp_links_for_selection) # Display fresh, unsorted list with numbers

    if not temp_links_for_selection:
        return

    try:
        choice_str = input("Enter the number of the link to edit: ").strip()
        if not choice_str:
            print("No selection made. Edit cancelled.")
            return
        choice = int(choice_str)

        if choice < 1 or choice > len(temp_links_for_selection):
            print("Invalid link number. Please try again.")
            return

        link_id_to_edit = temp_links_for_selection[choice - 1].get('id')
        
        # Load the main list to perform the edit
        links = load_links()
        link_to_edit_index = -1
        for i, link_obj in enumerate(links):
            if link_obj.get('id') == link_id_to_edit:
                link_to_edit_index = i
                break
        
        if link_to_edit_index == -1:
            print("Error: Link not found for editing.")
            return

        link_to_edit = links[link_to_edit_index] # This is the dictionary from the list 'links'

        print(f"\nEditing link: '{link_to_edit.get('title', 'N/A')}'")
        
        print(f"Current URL: {link_to_edit.get('url')}")
        new_url = input(f"Enter new URL (or press Enter to keep current): ").strip()
        if new_url and not (new_url.startswith("http://") or new_url.startswith("https://")):
            print("Invalid URL format. URL not changed.")
            new_url = link_to_edit.get('url')
        elif not new_url: # Empty input
            new_url = link_to_edit.get('url')

        print(f"Current Title: {link_to_edit.get('title')}")
        new_title = input(f"Enter new title (or press Enter to keep current): ").strip()
        if not new_title: # Empty input
            new_title = link_to_edit.get('title')
        
        print(f"Current Notes: {link_to_edit.get('notes', '')}") 
        new_notes_input = input("Enter new notes (or press Enter to keep current, type 'clear' to remove notes): ").strip()
        if new_notes_input.lower() == 'clear':
            new_notes = ''
        elif new_notes_input:
            new_notes = new_notes_input
        else: 
            new_notes = link_to_edit.get('notes', '')

        current_default_status = "y" if link_to_edit.get('is_default') else "n"
        print(f"Currently a default link: {current_default_status.upper()}")
        is_default_input = input(f"Make this a default link? (y/n, Enter to keep '{current_default_status}'): ").strip().lower()
        new_is_default = link_to_edit.get('is_default') 
        if is_default_input == 'y':
            new_is_default = True
        elif is_default_input == 'n':
            new_is_default = False

        # Update the link in the 'links' list directly
        links[link_to_edit_index]['url'] = new_url
        links[link_to_edit_index]['title'] = new_title if new_title else new_url
        links[link_to_edit_index]['notes'] = new_notes
        links[link_to_edit_index]['is_default'] = new_is_default
        # We should also update a 'modified_timestamp' if we add one.
        
        save_links(links) # Save the modified 'links' list
        print(f"Link updated successfully: '{links[link_to_edit_index]['title']}'")

    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"An unexpected error occurred during edit: {e}")
    print("-----------------")


def visit_link_interactive():
    # Similar logic to delete/edit for selecting the correct link
    print("\n--- Visit Link ---")
    temp_links_for_selection = load_links()
    if not temp_links_for_selection:
        print("No links available to visit.")
        return

    print("\n--- Select Link to Visit (from list below) ---")
    display_links(temp_links_for_selection) # Display fresh, unsorted list with numbers

    if not temp_links_for_selection:
        return
    
    try:
        choice_str = input("Enter the number of the link to mark as visited: ").strip()
        if not choice_str:
            print("No selection made. Visit cancelled.")
            return
            
        choice = int(choice_str)

        if choice < 1 or choice > len(temp_links_for_selection):
            print("Invalid link number. Please try again.")
            return

        link_id_to_visit = temp_links_for_selection[choice - 1].get('id')

        links = load_links()
        link_to_visit_index = -1
        for i, link_obj in enumerate(links):
            if link_obj.get('id') == link_id_to_visit:
                link_to_visit_index = i
                break
        
        if link_to_visit_index == -1:
            print("Error: Link not found to mark as visited.")
            return
        
        links[link_to_visit_index]['visit_count'] = links[link_to_visit_index].get('visit_count', 0) + 1
        links[link_to_visit_index]['last_visited_timestamp'] = int(time.time())
        
        save_links(links)
        
        visited_link_title = links[link_to_visit_index].get('title', 'N/A')
        visited_link_url = links[link_to_visit_index].get('url', 'N/A')
        print(f"Marked '{visited_link_title}' as visited.")
        print(f"URL: {visited_link_url}")
        
    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    print("------------------")


def search_links_interactive():
    """Searches links by keyword in title, URL, or notes, with optional sorting."""
    print("\n--- Search Links ---")
    search_term = input("Enter search term: ").strip().lower()

    if not search_term:
        print("Search term cannot be empty.")
        return

    all_links = load_links()
    if not all_links:
        print("No links available to search.")
        return

    filtered_links = []
    for link in all_links:
        title = link.get('title', '').lower()
        url = link.get('url', '').lower()
        notes = link.get('notes', '').lower()

        if search_term in title or search_term in url or search_term in notes:
            filtered_links.append(link)

    if not filtered_links:
        print(f"No links found matching '{search_term}'.")
    else:
        print(f"\nFound {len(filtered_links)} link(s) matching '{search_term}':")
        sort_by, sort_order = get_sort_preferences()
        display_links(filtered_links, sort_by=sort_by, sort_order=sort_order)
    print("--------------------")


def main_cli():
    """Main function to run the command-line interface."""
    while True:
        print("\nInteractive Link Manager")
        print("1. Add Link")
        print("2. View All Links")
        print("3. Delete Link")
        print("4. Edit Link")
        print("5. Visit Link")
        print("6. Search Links")
        print("7. Exit")
        choice = input("Enter your choice (1-7): ").strip()

        if choice == '1':
            add_link_interactive()
        elif choice == '2':
            view_all_links_interactive()
        elif choice == '3':
            delete_link_interactive()
        elif choice == '4':
            edit_link_interactive()
        elif choice == '5':
            visit_link_interactive()
        elif choice == '6':
            search_links_interactive()
        elif choice == '7':
            print("Exiting Link Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    main_cli()
