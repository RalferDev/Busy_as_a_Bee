import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from pynput.mouse import Controller, Button
from pynput.keyboard import Listener, Key
import os

# Variabili globali per controllare lo stato del clicker
mouse = Controller()  # Controller per il mouse
clicking_active = False  # Flag per indicare se il clicker è attivo
click_thread = None  # Thread per il processo di auto-clicking
keyboard_listener_thread = None  # Thread per il listener della tastiera (per l'hotkey)

# Valori predefiniti per intervallo e ripetizioni
default_interval = 60.0 # Intervallo predefinito in secondi
default_repetitions = 0  # Numero di ripetizioni predefinito (0 per infiniti click)


def auto_click_loop(interval, repetitions):
    """
    Simula i click del mouse in un ciclo, basandosi sull'intervallo e il numero di ripetizioni.
    Questa funzione viene eseguita in un thread separato per non bloccare l'interfaccia grafica.
    """
    global clicking_active
    count = 0

    # Per garantire che il primo click sia preceduto dall'intervallo,
    # eseguiamo la pausa all'inizio di ogni iterazione del ciclo.
    while clicking_active and (repetitions == 0 or count < repetitions):
        # Implementa uno "sleep" non bloccante: invece di dormire per l'intero intervallo,
        # dorme per brevi periodi e controlla il flag 'clicking_active' frequentemente.
        # Questo permette al clicker di fermarsi quasi istantaneamente quando richiesto.
        start_time = time.time()
        while time.time() - start_time < interval and clicking_active:
            time.sleep(0.05)  # Piccola pausa per consentire controlli frequenti

        # Se il clicker è stato disattivato durante la pausa, esci dal ciclo
        if not clicking_active:
            break

        mouse.click(Button.left)  # Esegue un click sinistro del mouse
        count += 1

        # Aggiorna lo stato nell'interfaccia grafica (ad esempio, il conteggio dei click)
        # Usiamo app.after(0, ...) per eseguire l'aggiornamento sul thread principale di Tkinter
        if repetitions > 0:
            app.after(0, lambda: status_label.config(text=f"Stato: Attivo ({count}/{repetitions} clic)",
                                                     foreground="#BD93F9"))  # Colore più luminoso per "attivo"

    # Se il ciclo è terminato a causa del raggiungimento del limite di ripetizioni (non per un arresto manuale)
    if clicking_active:
        app.after(0, stop_clicking)  # Chiama la funzione di stop sul thread principale di Tkinter


def start_clicking():
    """Avvia il processo di auto-clicking."""
    global clicking_active, click_thread
    if not clicking_active:  # Avvia solo se non è già attivo
        try:
            # Recupera i valori di intervallo e ripetizioni dagli input dell'utente
            interval = float(interval_var.get())
            repetitions = int(repetitions_var.get())

            # Validazione degli input
            if interval <= 0:
                messagebox.showerror("Errore", "L'intervallo deve essere maggiore di zero.")
                return
            if repetitions < 0:
                messagebox.showerror("Errore", "Il numero di ripetizioni non può essere negativo.")
                return

            # Imposta lo stato del clicker su attivo e aggiorna l'interfaccia grafica
            clicking_active = True
            status_label.config(text="WORKING", foreground="#FFDB38")  # Colore più luminoso per "attivo"
            # Linea modificata per applicare il nuovo stile 'Active.TButton'
            start_button.config(text="WORKING", command=stop_clicking,
                                style='Active.TButton')  # Cambia il testo e applica stile

            # Disabilita gli input mentre il clicker è attivo
            interval_entry.config(state='disabled')
            repetitions_entry.config(state='disabled')

            # Avvia la funzione 'auto_click_loop' in un nuovo thread
            click_thread = threading.Thread(target=auto_click_loop, args=(interval, repetitions))
            click_thread.daemon = True  # Imposta il thread come "daemon" per consentire al programma principale di chiudersi anche se il thread è ancora in esecuzione
            click_thread.start()
        except ValueError:
            messagebox.showerror("Errore", "Inserisci valori numerici validi per intervallo e ripetizioni.")
    else:
        # Se il clicker è già attivo, il pulsante funge da "Ferma"
        stop_clicking()


def stop_clicking():
    """Ferma il processo di auto-clicking."""
    global clicking_active, click_thread
    if clicking_active:  # Ferma solo se è attivo
        clicking_active = False  # Imposta il flag su False per segnalare al thread di click di fermarsi
        status_label.config(text="IDLE", foreground="#FF5555")  # Colore più scuro per "inattivo"
        # Linea che ripristina lo stile predefinito 'Dark.TButton'
        start_button.config(text="FREE", command=start_clicking,
                            style='Dark.TButton')  # Ripristina il testo e lo stile

        # Riabilita gli input quando il clicker è inattivo
        interval_entry.config(state='normal')
        repetitions_entry.config(state='normal')

        # Il thread 'auto_click_loop' uscirà automaticamente dal suo ciclo quando rileva che 'clicking_active' è False.


def on_press(key):
    """
    Funzione di callback per il listener della tastiera di pynput.
    Viene richiamata ogni volta che un tasto viene premuto.
    """
    global clicking_active
    try:
        # Controlla se il tasto premuto è F6
        if key == Key.f6:
            # Toggla lo stato del clicker chiamando la funzione sul thread principale di Tkinter
            app.after(0, lambda: on_hotkey_pressed())
    except AttributeError:
        # Gestisce i tasti speciali che non hanno un attributo '.char'
        pass


def on_hotkey_pressed():
    """Funzione che viene chiamata quando l'hotkey (F6) viene attivata."""
    if clicking_active:
        stop_clicking()
    else:
        start_clicking()


def setup_hotkey_listener():
    """Imposta e avvia il listener globale della tastiera in un thread separato."""
    global keyboard_listener_thread
    # Avvia il listener solo se non è già in esecuzione
    if keyboard_listener_thread is None or not keyboard_listener_thread.is_alive():
        keyboard_listener_thread = Listener(on_press=on_press)
        keyboard_listener_thread.daemon = True  # Cruciale per una chiusura pulita dell'applicazione
        keyboard_listener_thread.start()
        status_label_hotkey.config(text="Hotkey: F6",
                                   foreground="#8BE9FD")  # Colore per hotkey attiva
    else:
        status_label_hotkey.config(text="Hotkey già Attiva (F6)", foreground="#6A97A3")


# --- Configurazione dell'Interfaccia Grafica (GUI) ---
app = tk.Tk()

app.title("Busy as a Bee")
app.geometry("300x170")  # Ridotto l'altezza e la larghezza per renderla più compatta
app.resizable(False, False)  # Non ridimensionabile

# Inserimento dell'icona personalizzata
# Ottieni la directory corrente dello script per trovare il file icona
script_dir = os.path.dirname(__file__)
icon_path = os.path.join(script_dir, "icon1.ico") # Assicurati che 'icona.ico' sia nella stessa cartella

try:
    app.iconbitmap(icon_path)
except tk.TclError:
    # Gestisce il caso in cui il file icona non venga trovato o sia corrotto
    messagebox.showwarning("Icona mancante", f"Impossibile caricare l'icona da {icon_path}. Assicurati che il file 'icon1.ico' esista e sia valido.")


# Colori per il tema scuro (Dark Theme)
DARK_BG = "#282A36"  # Sfondo principale
LIGHT_TEXT = "#F8F8F2"  # Testo chiaro
ACCENT_COLOR = "#FFDB38"  # Colore di accento (viola)
BUTTON_BG = "#44475A"  # Sfondo pulsanti
BUTTON_FG = LIGHT_TEXT  # Testo pulsanti
ENTRY_BG = "#6272A4"  # Sfondo campi di input (blu-grigio)
ENTRY_FG = LIGHT_TEXT  # Testo campi di input

app.config(bg=DARK_BG)  # Imposta lo sfondo della finestra principale

# Stile ttk
app.style = ttk.Style()
app.style.theme_use('clam')  # Un tema neutro come base per le modifiche

# Configura stili personalizzati
app.style.configure('TFrame', background=DARK_BG)
app.style.configure('TLabel', background=DARK_BG, foreground=LIGHT_TEXT,
                    font=("Helvetica", 9))  # Font leggermente più piccolo
app.style.configure('Dark.TButton',
                    background=BUTTON_BG,
                    foreground=BUTTON_FG,
                    font=("Helvetica", 10, "bold"),
                    relief="flat",  # Rimuovi il bordo predefinito
                    padding=[10, 5])  # Ridotto il padding verticale per i pulsanti
app.style.map('Dark.TButton',
              background=[('active', ACCENT_COLOR)],  # Colore all'hover
              foreground=[('active', DARK_BG)])  # Testo al hover

# NUOVO STILE: Stile per il pulsante attivo (quando il clicker è in funzione)
app.style.configure('Active.TButton',
                    background='#FFDB38',  # Colore giallo richiesto
                    foreground=DARK_BG,    # Testo scuro per contrasto sul giallo
                    font=("Helvetica", 10, "bold"),
                    relief="flat",
                    padding=[10, 5])
app.style.map('Active.TButton',
              background=[('active', '#FFDB38'), ('pressed', '#FFDB38')], # Mantieni il colore giallo anche all'hover/pressione
              foreground=[('active', DARK_BG), ('pressed', DARK_BG)])


# Frame principale che contiene tutto per un layout più controllato
main_frame = ttk.Frame(app, padding="15")  # Ridotto il padding generale
main_frame.pack(expand=True, fill="both")  # Espande per riempire la finestra

# Input per l'intervallo
ttk.Label(main_frame, text="Range (sec):").grid(row=0, column=0, padx=5, pady=3, sticky="w")  # Padding ridotto
interval_var = tk.DoubleVar(value=default_interval)
interval_entry = ttk.Entry(main_frame, textvariable=interval_var, width=10)  # Larghezza ridotta
interval_entry.grid(row=0, column=1, padx=5, pady=3, sticky="ew")

# Input per le ripetizioni
ttk.Label(main_frame, text="Repetitions (0=inf):").grid(row=1, column=0, padx=5, pady=3, sticky="w")  # Padding ridotto
repetitions_var = tk.IntVar(value=default_repetitions)
repetitions_entry = ttk.Entry(main_frame, textvariable=repetitions_var, width=10)  # Larghezza ridotta
repetitions_entry.grid(row=1, column=1, padx=5, pady=3, sticky="ew")

# Configurazione delle colonne per espansione
main_frame.columnconfigure(1, weight=1)

# Pulsante Avvia/Ferma Clic
start_button = ttk.Button(main_frame, text="FREE", command=start_clicking, style='Dark.TButton')
start_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")  # Occupa entrambe le colonne e centrato

# Etichette di stato
status_label = ttk.Label(main_frame, text="IDLE", font=("Helvetica", 11, "bold"), foreground="#FF5555")
status_label.grid(row=3, column=0, columnspan=2, pady=(5, 0))  # Centrato
status_label_hotkey = ttk.Label(main_frame, text="Hotkey: Inattiva", font=("Helvetica", 9), foreground="#A3A3A3")
status_label_hotkey.grid(row=4, column=0, columnspan=2, pady=(0, 5))  # Centrato

# --- Avvio iniziale ---
# Avvia il listener dell'hotkey poco dopo che la GUI è stata impostata,
# per evitare di bloccare il processo di avvio dell'interfaccia.
app.after(100, setup_hotkey_listener) # Rimosso il tuple vuoto '()'


# Funzione per gestire la chiusura della finestra in modo elegante
def on_closing():
    global clicking_active
    clicking_active = False  # Segnala al thread di click di fermarsi

    # Ferma esplicitamente il listener della tastiera
    if keyboard_listener_thread is not None and keyboard_listener_thread.is_alive():
        keyboard_listener_thread.stop()  # Importante per rilasciare le risorse di sistema

    app.destroy()  # Distrugge la finestra dell'applicazione


# Associa la funzione on_closing all'evento di chiusura della finestra
app.protocol("WM_DELETE_WINDOW", on_closing)

# Avvia il loop principale dell'applicazione Tkinter
app.mainloop()
