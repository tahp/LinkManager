# app.py

from flask import Flask, render_template, request, redirect, url_for, flash
import link_core # Your refactored core logic
import os
from datetime import datetime as dt # Aliased to avoid conflict with Jinja filter
import time

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Custom Jinja2 Filter for datetime formatting ---
def format_datetime_filter(value, fmt=None):
    if value == "now":
        value = dt.now()
    if not isinstance(value, dt): 
        try: 
            value = dt.fromtimestamp(int(value))
        except (ValueError, TypeError, OSError): 
            try:
                value = dt.fromisoformat(str(value))
            except (ValueError, TypeError):
                 return str(value) 

    if fmt:
        return value.strftime(fmt)
    return value.strftime(link_core.get_active_date_format_str())
app.jinja_env.filters['datetime'] = format_datetime_filter


# --- Helper for timestamp to date/time string conversion ---
def _ts_to_datetime_strings(timestamp):
    if not timestamp or timestamp == 0:
        return "", "" 
    try:
        dt_obj = dt.fromtimestamp(timestamp) 
        return dt_obj.strftime('%Y-%m-%d'), dt_obj.strftime('%H:%M')
    except (ValueError, TypeError, OSError):
        return "", ""

@app.context_processor
def inject_global_vars():
    if not link_core.CONFIG:
        print("Warning: link_core.CONFIG not loaded. Attempting to load now.")
        link_core.load_config()
    return dict(
        APP_CONFIG=link_core.CONFIG,
        format_timestamp=link_core.format_web_timestamp
    )

@app.route('/')
@app.route('/links')
def index():
    all_links = link_core.get_all_links()

    # Determine sort parameters
    # Default sort is by reminder_time (ascending: soonest first, then those without reminders)
    # User can override by clicking table headers
    sort_by_param = request.args.get('sort_by')
    sort_order_param = request.args.get('sort_order')

    if sort_by_param:
        current_sort_by = sort_by_param
        current_sort_order = sort_order_param if sort_order_param in ['asc', 'desc'] else 'asc'
    else:
        # Default sort criteria
        current_sort_by = 'reminder_time'
        current_sort_order = 'asc' 
    
    # Apply sorting
    # The core_sort_links function will handle the actual sorting logic
    # including how 'reminder_time' handles timestamps of 0.
    displayable_links_intermediate = link_core.core_sort_links(all_links, current_sort_by, current_sort_order)
    
    page = request.args.get('page', 1, type=int)
    page_size = link_core.CONFIG.get('page_size', 20) # Default page size from config
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    
    paginated_links_slice = displayable_links_intermediate[start_index:end_index]
    
    processed_paginated_links = []
    for link in paginated_links_slice:
        link_copy = link.copy()
        link_copy['reminder_status_info'] = link_core.get_daily_time_status(link_copy.get('reminder_timestamp', 0))
        processed_paginated_links.append(link_copy)
        
    total_pages = (len(displayable_links_intermediate) + page_size - 1) // page_size
    
    return render_template('index.html',
                           links=processed_paginated_links,
                           current_page=page,
                           total_pages=total_pages,
                           sort_by=current_sort_by, # Pass the effective sort parameters to template
                           sort_order=current_sort_order)


# ... (add_link_form, add_link_action, edit_link_form, delete_link_action, settings_page, visit_link_action as before) ...
@app.route('/add', methods=['GET'])
def add_link_form():
    return render_template('add_link.html',
                           url=request.args.get('url', ''),
                           title=request.args.get('title', ''),
                           notes=request.args.get('notes', ''),
                           is_default_val=request.args.get('is_default_val'),
                           reminder_time=request.args.get('reminder_time', ''))

@app.route('/add', methods=['POST'])
def add_link_action():
    url = request.form.get('url', '').strip()
    title = request.form.get('title', '').strip()
    notes = request.form.get('notes', '').strip() 
    is_default_val = request.form.get('is_default') 
    is_default = (is_default_val == 'yes')
    reminder_time_str = request.form.get('reminder_time', "").strip()
    reminder_ts = 0
    if reminder_time_str: 
        try:
            parsed_time_obj = dt.strptime(reminder_time_str, '%H:%M').time()
            todays_date = dt.now().date()
            reminder_dt_obj = dt.combine(todays_date, parsed_time_obj)
            current_system_dt = dt.now()
            if reminder_dt_obj < current_system_dt and (current_system_dt - reminder_dt_obj).total_seconds() > 60:
                flash("Warning: Reminder time is in the past for today.", "warning")
            reminder_ts = int(reminder_dt_obj.timestamp())
        except ValueError:
            flash("Invalid reminder time format. Reminder not set.", "error")
            reminder_ts = 0 
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        flash("URL is required and must start with http:// or https://.", "error")
        return render_template('add_link.html', url=url, title=title, notes=notes, 
                               is_default_val=is_default_val,
                               reminder_time=reminder_time_str), 400
    result = link_core.add_new_link(
        url=url, title=title, notes=notes, is_default=is_default, reminder_timestamp=reminder_ts
    )
    if isinstance(result, dict): 
        new_link_title = result.get('title', result.get('url'))
        flash(f"Link '{new_link_title}' added successfully!", "success")
        return redirect(url_for('index'))
    elif result == "duplicate_url":
        flash(f"The URL '{url}' already exists. Link not added.", "error")
        return render_template('add_link.html', 
                               url=url, title=title, notes=notes,
                               is_default_val=request.form.get('is_default'), 
                               reminder_time=reminder_time_str
                              ), 409 
    else: 
        flash("Failed to add link. An internal error occurred.", "error")
        return render_template('add_link.html', 
                               url=url, title=title, notes=notes,
                               is_default_val=request.form.get('is_default'),
                               reminder_time=reminder_time_str
                               ), 500

@app.route('/edit/<link_id>', methods=['GET', 'POST'])
def edit_link_form(link_id):
    link_to_edit = link_core.get_link_by_id(link_id)
    if not link_to_edit:
        flash(f"Error: Link with ID {link_id} not found.", "error")
        return redirect(url_for('index'))
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        title = request.form.get('title', '').strip()
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            flash("URL is required and must start with http:// or https://.", "error")
            _original_date_str, original_time_str = _ts_to_datetime_strings(link_to_edit.get('reminder_timestamp', 0))
            submitted_reminder_time_val = request.form.get('reminder_time', original_time_str)
            current_form_state_for_link = {
                'id': link_id, 'url': url, 'title': title,
                'notes': link_to_edit.get('notes', ''), 
                'is_default': link_to_edit.get('is_default', False) 
            }
            return render_template('edit_link.html', 
                                   link=current_form_state_for_link,
                                   reminder_time_val=submitted_reminder_time_val,
                                   error_source='validation'), 400
        original_reminder_ts = link_to_edit.get('reminder_timestamp', 0)
        new_reminder_ts = original_reminder_ts 
        submitted_reminder_time_str = request.form.get('reminder_time', "").strip()
        if not submitted_reminder_time_str:
            if original_reminder_ts != 0: 
                 flash("Reminder time cleared.", "info")
            new_reminder_ts = 0
        else:
            try:
                parsed_time_obj = dt.strptime(submitted_reminder_time_str, '%H:%M').time()
                target_date_for_reminder = None
                if original_reminder_ts != 0:
                    original_reminder_dt_obj = dt.fromtimestamp(original_reminder_ts)
                    target_date_for_reminder = original_reminder_dt_obj.date()
                else:
                    target_date_for_reminder = dt.now().date()
                new_reminder_dt_obj = dt.combine(target_date_for_reminder, parsed_time_obj)
                new_reminder_ts = int(new_reminder_dt_obj.timestamp())
                current_system_dt = dt.now()
                if new_reminder_dt_obj < current_system_dt and (current_system_dt - new_reminder_dt_obj).total_seconds() > 60:
                     flash("Warning: Reminder time is in the past (considering its date).", "warning")
            except ValueError:
                flash("Invalid reminder time format. Reminder remains unchanged from its original value.", "error")
                new_reminder_ts = original_reminder_ts 
        updated_data = {
            "url": url, "title": title if title else url, 
            "reminder_timestamp": new_reminder_ts
        }
        updated_link_obj = link_core.update_link(link_id, updated_data)
        if updated_link_obj:
            flash(f"Link '{updated_link_obj.get('title', updated_link_obj.get('url'))}' updated successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("Failed to update link. An internal error occurred during save.", "error")
            current_form_state_for_link = {
                'id': link_id, 'url': url, 'title': title,
                'notes': link_to_edit.get('notes', ''),
                'is_default': link_to_edit.get('is_default', False)
            }
            _new_date_val, new_time_val = _ts_to_datetime_strings(new_reminder_ts)
            return render_template('edit_link.html', 
                                   link=current_form_state_for_link,
                                   reminder_time_val=new_time_val,
                                   error_source='save_fail'), 500
    else: # GET request
        _date_str_val, time_str_val = _ts_to_datetime_strings(link_to_edit.get('reminder_timestamp'))
        return render_template('edit_link.html', 
                               link=link_to_edit, 
                               reminder_time_val=time_str_val)

@app.route('/delete/<link_id>', methods=['POST'])
def delete_link_action(link_id):
    link_to_delete = link_core.get_link_by_id(link_id)
    if not link_to_delete:
        flash(f"Error: Link with ID {link_id} not found. Cannot delete.", "error")
        return redirect(url_for('index'))
    link_display_name = link_to_delete.get('title', '').strip()
    if not link_display_name:
        link_display_name = link_to_delete.get('url', f"ID {link_id}")
    if link_core.delete_link_by_id(link_id):
        flash(f"Link '{link_display_name}' deleted successfully.", "success")
    else:
        flash(f"Failed to delete link '{link_display_name}'. An internal error may have occurred or the link was already removed.", "error")
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
    if request.method == 'POST':
        try:
            page_size_str = request.form.get('page_size')
            page_size = int(page_size_str)
            if page_size <= 0 or page_size > 100:
                raise ValueError("Page size out of range.")
            link_core.CONFIG['page_size'] = page_size
        except (ValueError, TypeError):
            flash("Invalid Page Size. Please enter a number between 1 and 100.", "error")
            return render_template('settings.html',
                                   current_settings=link_core.CONFIG,
                                   all_date_formats=link_core.CONFIG.get('date_formats', {}))
        date_format_choice = request.form.get('date_format_choice')
        if date_format_choice not in link_core.CONFIG.get('date_formats', {}):
            flash("Invalid Date Format selected.", "error")
            return render_template('settings.html',
                                   current_settings=link_core.CONFIG,
                                   all_date_formats=link_core.CONFIG.get('date_formats', {}))
        link_core.CONFIG['date_format_choice'] = date_format_choice
        default_export_path = request.form.get('default_export_path', '~/' ).strip()
        link_core.CONFIG['default_export_path'] = default_export_path
        if link_core.save_config():
            flash("Settings saved successfully!", "success")
        else:
            flash("Error saving settings. Please try again.", "error")
        return redirect(url_for('settings_page'))
    if not link_core.CONFIG: 
        link_core.load_config()
    return render_template('settings.html',
                           current_settings=link_core.CONFIG,
                           all_date_formats=link_core.CONFIG.get('date_formats', {}))

@app.route('/visit/<link_id>', methods=['GET'])
def visit_link_action(link_id):
    link_details = link_core.get_link_by_id(link_id)
    if not link_details:
        flash("Link not found. Cannot record visit.", "error")
        return redirect(url_for('index'))
    target_url = link_details.get('url')
    if not target_url: 
        flash("Error: The selected link does not have a valid URL associated with it.", "error")
        return redirect(url_for('index'))
    if link_core.record_link_visit(link_id):
        print(f"Redirecting to: {target_url} for link ID {link_id}")
        return redirect(target_url)
    else:
        flash("Could not record visit for the link due to an internal error. Please try again.", "error")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

