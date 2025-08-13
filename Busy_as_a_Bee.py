import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from pynput.mouse import Controller, Button
from pynput.keyboard import Listener, Key, KeyCode  # Imported KeyCode to handle character keys

import os

# Global variables to control the clicker state
mouse = Controller()  # Mouse controller
clicking_active = False  # Flag to indicate if the clicker is active
click_thread = None  # Thread for the auto-clicking process
keyboard_listener_thread = None  # Thread for the main hotkey listener
hotkey_capture_listener = None  # Temporary listener for new hotkey capture
current_hotkey = Key.f6  # Initial default hotkey (now a global variable)

# Default values for interval and repetitions
default_interval = 60 # Default interval in seconds
default_repetitions = 0  # Default number of repetitions (0 for infinite clicks)


# noinspection PyTypeChecker
def auto_click_loop(interval, repetitions):
    """
    Simulates mouse clicks in a loop, based on the interval and number of repetitions.
    This function runs in a separate thread to avoid blocking the graphical interface.
    """
    global clicking_active
    count = 0

    # To ensure the first click is preceded by the interval,
    # we perform the pause at the beginning of each loop iteration.
    while clicking_active and (repetitions == 0 or count < repetitions):
        # Implements a non-blocking "sleep": instead of sleeping for the entire interval,
        # it sleeps for short periods and frequently checks the 'clicking_active' flag.
        # This allows the clicker to stop almost instantly when requested.
        start_time = time.time()
        while time.time() - start_time < interval and clicking_active:
            time.sleep(0.05)  # Small pause to allow frequent checks

        # If the clicker was deactivated during the pause, exit the loop
        if not clicking_active:
            break

        mouse.click(Button.left)  # Performs a left mouse click
        count += 1

        # Updates the status in the graphical interface (e.g., click count)
        # We use app.after(0, ...) to run the update on the main Tkinter thread
        if repetitions > 0:
            # noinspection PyTypeChecker
            app.after(0, lambda: status_label.config(text=f"Stato: Attivo ({count}/{repetitions} clic)",
                                                     foreground="#BD93F9"))  # Brighter color for "active"

    # If the loop ended due to reaching the repetition limit (not by manual stop)
    if clicking_active:
        app.after(0, stop_clicking)  # Calls the stop function on the main Tkinter thread


def start_clicking():
    """Starts the auto-clicking process."""
    global clicking_active, click_thread
    if not clicking_active:  # Starts only if not already active
        try:
            # Retrieves interval and repetition values from user input
            interval = float(interval_var.get())
            repetitions = int(repetitions_var.get())

            # Input validation
            if interval <= 0:
                messagebox.showerror("Errore", "L'intervallo deve essere maggiore di zero.")
                return
            if repetitions < 0:
                messagebox.showerror("Errore", "Il numero di ripetizioni non può essere negativo.")
                return

            # Sets the clicker status to active and updates the GUI
            clicking_active = True
            status_label.config(text="WORKING", foreground="#FFDB38")  # Brighter color for "active"
            start_button.config(text="STOP WORKING", command=stop_clicking,
                                style='Active.TButton')  # Changes text and applies style

            # Disables inputs and the hotkey change button while the clicker is active
            interval_entry.config(state='disabled')
            repetitions_entry.config(state='disabled')
            # Checks if change_hotkey_button has been created before disabling it
            if 'change_hotkey_button' in globals() and change_hotkey_button.winfo_exists():
                change_hotkey_button.config(state='disabled')

            # Starts the 'auto_click_loop' function in a new thread
            click_thread = threading.Thread(target=auto_click_loop, args=(interval, repetitions))
            click_thread.daemon = True  # Sets the thread as "daemon" to allow the main program to close even if the thread is still running
            click_thread.start()
        except ValueError:
            messagebox.showerror("Errore", "Inserisci valori numerici validi per intervallo e ripetizioni.")
    else:
        # If the clicker is already active, the button acts as "Stop"
        stop_clicking()


def stop_clicking():
    """Stops the auto-clicking process."""
    global clicking_active, click_thread
    if clicking_active:  # Stops only if active
        clicking_active = False  # Sets the flag to False to signal the click thread to stop
        status_label.config(text="Bzzing Around", foreground="#FF5555")  # Darker color for "inactive"
        start_button.config(text="GO TO WORK", command=start_clicking,
                            style='Dark.TButton')  # Restores text and style

        # Re-enables inputs and the hotkey change button when the clicker is inactive
        interval_entry.config(state='normal')
        repetitions_entry.config(state='normal')
        # Checks if change_hotkey_button has been created before enabling it
        if 'change_hotkey_button' in globals() and change_hotkey_button.winfo_exists():
            change_hotkey_button.config(state='normal')

        # The 'auto_click_loop' thread will automatically exit its loop when it detects 'clicking_active' is False.


def on_hotkey_pressed():
    """Function called when the hotkey (F6) is activated."""
    if clicking_active:
        stop_clicking()
    else:
        start_clicking()


def on_press(key):
    """
    Callback function for the pynput keyboard listener.
    It is called every time a key is pressed.
    """
    global clicking_active, current_hotkey

    # This check handles both 'Key' (special keys) and 'KeyCode' (normal characters) keys
    # Checks if the pressed key matches the current hotkey
    if key == current_hotkey:
        app.after(0, on_hotkey_pressed)
    elif isinstance(current_hotkey, KeyCode) and hasattr(key, 'char') and key.char:
        # Handles the case where the hotkey is a character (e.g., 'a') and the pressed key is a character
        if key.char.lower() == current_hotkey.char.lower():
            app.after(0, on_hotkey_pressed)


def setup_hotkey_listener():
    """Sets up and starts the global keyboard listener in a separate thread."""
    global keyboard_listener_thread
    # Stops the existing listener if active to restart it with the new hotkey
    if keyboard_listener_thread is not None and keyboard_listener_thread.is_alive():
        keyboard_listener_thread.stop()
        keyboard_listener_thread.join()  # Ensures the thread has terminated

    keyboard_listener_thread = Listener(on_press=on_press)
    keyboard_listener_thread.daemon = True  # Crucial for a clean application shutdown
    keyboard_listener_thread.start()
    update_hotkey_status_label()  # Updates the label to show the current hotkey


def update_hotkey_status_label():
    """Updates the hotkey status label with the current key."""
    global current_hotkey
    key_name = ""
    if hasattr(current_hotkey, 'name'):
        key_name = current_hotkey.name.upper()  # For special keys like 'f6', 'space', etc.
    elif hasattr(current_hotkey, 'char'):
        key_name = current_hotkey.char.upper()  # For normal characters
    else:
        key_name = str(current_hotkey).upper()  # Fallback for other cases

    status_label_hotkey.config(text=f"Hotkey: {key_name}", foreground="#8BE9FD")


def start_hotkey_capture():
    """
    Starts the new hotkey capture mode.
    Temporarily disables the main user interface and starts a dedicated listener
    to capture the next key pressed.
    """
    global hotkey_capture_listener, keyboard_listener_thread

    # Disables all interactive GUI elements
    start_button.config(state='disabled')
    interval_entry.config(state='disabled')
    repetitions_entry.config(state='disabled')
    change_hotkey_button.config(state='disabled')  # Disables itself as well

    status_label.config(text="SET HOTKEY", foreground="#FFDB38")
    status_label_hotkey.config(text="Press any key...", foreground="#BD93F9")

    # Stops the main keyboard listener to avoid conflicts during capture
    if keyboard_listener_thread is not None and keyboard_listener_thread.is_alive():
        keyboard_listener_thread.stop()
        keyboard_listener_thread.join()  # Waits for the thread to stop

    # Starts a temporary listener that waits for a single key press
    hotkey_capture_listener = Listener(on_press=on_key_for_hotkey_capture)
    hotkey_capture_listener.daemon = True
    hotkey_capture_listener.start()


def on_key_for_hotkey_capture(key):
    """
    Callback for the temporary listener that captures the new hotkey.
    """
    global current_hotkey, hotkey_capture_listener

    # Stops the temporary listener immediately after the first key press
    # Removed hotkey_capture_listener.join() to avoid RuntimeError
    if hotkey_capture_listener is not None and hotkey_capture_listener.is_alive():
        hotkey_capture_listener.stop()
        # hotkey_capture_listener.join() # This line was removed to fix the error

    current_hotkey = key  # Sets the captured key as the new hotkey
    hotkey_capture_listener = None  # Resets the temporary listener reference

    # Restarts the GUI and the main listener
    app.after(0, finish_hotkey_capture)


def finish_hotkey_capture():
    """
    Restores the GUI and restarts the main listener after hotkey capture.
    """
    # Re-enables interactive GUI elements
    start_button.config(state='normal')
    interval_entry.config(state='normal')
    repetitions_entry.config(state='normal')
    change_hotkey_button.config(state='normal')  # Re-enables the hotkey change button

    status_label.config(text="Bzzing Around", foreground="#FF5555")  # Restores IDLE status
    setup_hotkey_listener()  # Restarts the main listener with the new hotkey


# --- GUI Configuration ---
app = tk.Tk()

app.title("Busy as a Bee")
app.geometry("300x215")  # Slightly increased height to accommodate the new button
app.resizable(False, False)  # Not resizable

# Inserting custom icon
# Gets the current script directory to find the icon file
script_dir = os.path.dirname(__file__)
icon_path = os.path.join(script_dir, "icon1.ico")  # Make sure 'icon1.ico' is in the same folder

try:
    app.iconbitmap(icon_path)
except tk.TclError:
    # Handles the case where the icon file is not found or is corrupted
    messagebox.showwarning("Icon Missing",
                           f"Unable to load icon from {icon_path}. Make sure the file 'icon1.ico' exists and is valid.")

# Colors for the dark theme
DARK_BG = "#282A36"  # Main background (restored)
LIGHT_TEXT = "#F8F8F2"  # Light text
ACCENT_COLOR = "#FFDB38"  # Accent color (yellow)
BUTTON_BG = "#44475A"  # Button background (restored)
BUTTON_FG = LIGHT_TEXT  # Button text
ENTRY_BG = "#6272A4"  # Input field background (restored)
ENTRY_FG = LIGHT_TEXT  # Input field text

app.config(bg=DARK_BG)  # Sets the main window background

# ttk Style
app.style = ttk.Style()
app.style.theme_use('clam')  # A neutral theme as a base for modifications

# Configure custom styles
app.style.configure('TFrame', background=DARK_BG)
app.style.configure('TLabel', background=DARK_BG, foreground=LIGHT_TEXT,
                    font=("Helvetica", 9))  # Slightly smaller font
app.style.configure('Dark.TButton',
                    background=BUTTON_BG,
                    foreground=BUTTON_FG,
                    font=("Helvetica", 10, "bold"),
                    relief="flat",  # Removes default border
                    padding=[10, 5])  # Reduced vertical padding for buttons
app.style.map('Dark.TButton',
              background=[('active', ACCENT_COLOR)],  # Color on hover
              foreground=[('active', DARK_BG)])  # Text on hover

# NEW STYLE: Style for the active button (when the clicker is running)
app.style.configure('Active.TButton',
                    background='#FFDB38',  # Required yellow color
                    foreground=DARK_BG,  # Dark text for contrast on yellow
                    font=("Helvetica", 10, "bold"),
                    relief="flat",
                    padding=[10, 5])
app.style.map('Active.TButton',
              background=[('active', '#FFDB38'), ('pressed', '#FFDB38')],
              # Keep yellow color also on hover/press
              foreground=[('active', DARK_BG), ('pressed', DARK_BG)])

app.style.configure('TEntry', fieldbackground=ENTRY_BG, foreground=ENTRY_FG, insertbackground=LIGHT_TEXT)

# Main frame containing everything for a more controlled layout
main_frame = ttk.Frame(app, padding="15")  # Reduced general padding
main_frame.pack(expand=True, fill="both")  # Expands to fill the window

# Input for interval
ttk.Label(main_frame, text="Range (sec):").grid(row=0, column=0, padx=5, pady=3, sticky="w")  # Reduced padding
interval_var = tk.DoubleVar(value=default_interval)
interval_entry = ttk.Entry(main_frame, textvariable=interval_var, width=10)  # Reduced width
interval_entry.grid(row=0, column=1, padx=5, pady=3, sticky="ew")

# Input for repetitions
ttk.Label(main_frame, text="Repeat (0=inf):").grid(row=1, column=0, padx=5, pady=3, sticky="w")  # Reduced padding
repetitions_var = tk.IntVar(value=default_repetitions)
repetitions_entry = ttk.Entry(main_frame, textvariable=repetitions_var, width=10)  # Reduced width
repetitions_entry.grid(row=1, column=1, padx=5, pady=3, sticky="ew")

# Column configuration for expansion
main_frame.columnconfigure(1, weight=1)

# Start/Stop Click Button
start_button = ttk.Button(main_frame, text="GO TO WORK", command=start_clicking, style='Dark.TButton')
start_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")  # Occupies both columns and centered

# Status labels
status_label = ttk.Label(main_frame, text="Bzzing Around", font=("Helvetica", 11, "bold"), foreground="#FF5555")
status_label.grid(row=4, column=0, columnspan=2, pady=(5, 0))  # Centered
status_label_hotkey = ttk.Label(main_frame, text="Hotkey: Inattiva", font=("Helvetica", 9), foreground="#A3A3A3")
status_label_hotkey.grid(row=5, column=0, columnspan=2, pady=(0, 5))  # Centered

# New button to set hotkey
change_hotkey_button = ttk.Button(main_frame, text="Set Hotkey", command=start_hotkey_capture, style='Dark.TButton')
change_hotkey_button.grid(row=3, column=0, columnspan=2, pady=(5, 0), sticky="ew")

# --- Initial startup ---
# Starts the hotkey listener shortly after the GUI is set up,
# to avoid blocking the GUI startup process.
app.after(100, setup_hotkey_listener)


# Function to handle graceful window closing
def on_closing():
    global clicking_active
    clicking_active = False  # Signals the click thread to stop

    # Explicitly stops the main keyboard listener
    if keyboard_listener_thread and keyboard_listener_thread.is_alive():
        keyboard_listener_thread.stop()  # Important for releasing system resources
        keyboard_listener_thread.join()

    # Explicitly stops the temporary hotkey capture listener
    if hotkey_capture_listener and hotkey_capture_listener.is_alive():
        hotkey_capture_listener.stop()
        # Do not call .join() here, as the thread might be the current one
        # hotkey_capture_listener.join()

    app.destroy()  # Destroys the application window


# Associates the on_closing function with the window close event
app.protocol("WM_DELETE_WINDOW", on_closing)

# Starts the main Tkinter application loop
app.mainloop()
