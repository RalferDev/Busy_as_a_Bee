# 🐝 Busy as a Bee: Mouse Click Simulator

"Busy as a Bee" is a small and practical Python application with a graphical user interface (GUI) designed to simulate mouse clicks automatically. It's perfect for repetitive tasks or anyone needing to automate mouse clicks.

---

## Key Features 🚀

* **Automatic Mouse Clicking:** Performs left mouse clicks at the current cursor position.

* **Adjustable Interval:** You can set the waiting time between clicks, with a default value of **60 seconds**. This gives you full control over the clicking speed.

* **Number of Repetitions:** Define how many times the application should click. Setting **0** for repetitions means the clicker will run indefinitely until you stop it manually.

* **Customizable Hotkey:** Start or stop the clicker anytime with a keyboard shortcut (Hotkey), even when the application isn't in focus. The default hotkey is the **F6** key.

* **Hotkey Selection via GUI:** A unique feature allows you to easily change the hotkey directly from the graphical interface. Just click the "Set Hotkey" button and press your desired key.

* **Visual:** The interface clearly shows the clicker's status ("IDLE", "WORKING") when the clicker starts to give you auditory feedback.

* **Modern and Compact Interface:** The GUI is designed with a dark theme, compact elements, and a clean layout for a pleasant user experience.

---

## How to Use the App ⚙️

1.  **Launch**

2.  **Set Interval and Repetitions:** Use the "Range (sec)" and "Repeat (0=inf)" input fields to define the desired clicking speed and number of clicks.

3.  **Start/Stop Click:** Click the **"GO TO WORK"** button to start the click simulation. The button will change to **"STOP WORKING"** and turn yellow to indicate it's active. Click it again (or press the hotkey) to stop the clicker.

4.  **Change Hotkey:** Click the **"Set Hotkey"** button. The application will enter listening mode: simply press the key you want to use as the new hotkey. The listener will automatically stop after the key press, and the new hotkey will be active.

5.  **Status Monitoring:** The status label will provide real-time information on the clicker's activity and the current hotkey.

---

## Requirements 📦

To run the application, make sure you have Python installed and the following libraries:

* `pynput` (for mouse and keyboard control)


You'll also need:

* An icon file named `icon1.ico` in the same directory as the script to display the custom window icon.
