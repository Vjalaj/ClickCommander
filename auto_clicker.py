import time
import threading
import keyboard
import pyautogui
import csv
import os
from pynput import mouse, keyboard as pynkey

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

events = []
recordings = {}
current_recording_name = None
recording = False
playing = False
start_time = None
play_thread = None
RECORDINGS_DIR = "recordings"


def record_mouse():
    global recording, start_time, events
    events = []
    start_time = time.time()
    recording = True

    last_pos = pyautogui.position()
    last_drag_pos = None
    button_down = {}

    def on_move(x, y):
        if not recording:
            return False
        nonlocal last_pos, last_drag_pos
        t = time.time() - start_time
        if any(button_down.values()):
            events.append(("drag", x, y, t))
            last_drag_pos = (x, y)
        else:
            events.append(("move", x, y, t))
        last_pos = (x, y)

    def on_click(x, y, button, pressed):
        if not recording:
            return False
        t = time.time() - start_time
        btn = "left" if button == mouse.Button.left else "right" if button == mouse.Button.right else "middle"
        if pressed:
            button_down[btn] = True
            events.append(("press", x, y, btn, t))
        else:
            button_down[btn] = False
            events.append(("release", x, y, btn, t))

    def on_scroll(x, y, dx, dy):
        if not recording:
            return False
        t = time.time() - start_time
        # Multiply by 120 to get actual scroll units (Windows standard)
        scroll_amount = int(dy * 120) if dy != 0 else int(dx * 120)
        events.append(("scroll", x, y, scroll_amount, t))

    def on_key_press(key):
        if not recording:
            return False
        t = time.time() - start_time
        try:
            events.append(("key", key.char, t))
        except AttributeError:
            events.append(("key_special", str(key), t))

    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    key_listener = pynkey.Listener(on_press=on_key_press)
    
    mouse_listener.start()
    key_listener.start()
    
    while recording:
        time.sleep(0.01)
    
    mouse_listener.stop()
    key_listener.stop()

    print(f"\n[✓] Recorded {len(events)} events.")


def save_recording_to_csv(name, events_list):
    """Save recording to CSV file"""
    if not os.path.exists(RECORDINGS_DIR):
        os.makedirs(RECORDINGS_DIR)
    
    filepath = os.path.join(RECORDINGS_DIR, f"{name}.csv")
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["event_type", "param1", "param2", "param3", "param4", "timestamp"])
        for event in events_list:
            writer.writerow(event)
    print(f"[💾] Recording saved to {filepath}")


def load_recording_from_csv(name):
    """Load recording from CSV file"""
    filepath = os.path.join(RECORDINGS_DIR, f"{name}.csv")
    if not os.path.exists(filepath):
        return None
    
    events_list = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            # Convert back to appropriate types
            event_type = row[0]
            if event_type in ["move", "drag"]:
                events_list.append((event_type, int(row[1]), int(row[2]), float(row[5])))
            elif event_type in ["press", "release"]:
                events_list.append((event_type, int(row[1]), int(row[2]), row[3], float(row[5])))
            elif event_type == "scroll":
                events_list.append((event_type, int(row[1]), int(row[2]), int(row[3]), float(row[5])))
            elif event_type == "key":
                events_list.append((event_type, row[1] if row[1] != "None" else None, float(row[5])))
            elif event_type == "key_special":
                events_list.append((event_type, row[1], float(row[5])))
    
    print(f"[📂] Recording loaded from {filepath}")
    return events_list


def list_recordings():
    """List all saved recordings"""
    if not os.path.exists(RECORDINGS_DIR):
        return []
    
    files = [f[:-4] for f in os.listdir(RECORDINGS_DIR) if f.endswith('.csv')]
    return files


def play_events(repeat, gap):
    global playing
    playing = True
    for i in range(repeat):
        if not playing:
            return i  # Return current iteration when stopped
        print(f"[▶] Run {i + 1}/{repeat}")
        prev_time = 0
        for event in events:
            if not playing:
                return i  # Return current iteration when stopped
            t = event[-1]
            sleep_time = max(0, (t - prev_time))
            time.sleep(sleep_time)
            prev_time = t

            if event[0] == "move":
                pyautogui.moveTo(event[1], event[2], duration=0)
            elif event[0] == "drag":
                pyautogui.moveTo(event[1], event[2], duration=0)
            elif event[0] == "press":
                btn = event[3]
                pyautogui.moveTo(event[1], event[2], duration=0)
                if btn == "left":
                    pyautogui.mouseDown(button="left")
                elif btn == "right":
                    pyautogui.mouseDown(button="right")
                elif btn == "middle":
                    pyautogui.mouseDown(button="middle")
            elif event[0] == "release":
                btn = event[3]
                pyautogui.moveTo(event[1], event[2], duration=0)
                if btn == "left":
                    pyautogui.mouseUp(button="left")
                elif btn == "right":
                    pyautogui.mouseUp(button="right")
                elif btn == "middle":
                    pyautogui.mouseUp(button="middle")
            elif event[0] == "scroll":
                scroll_amount = event[3]
                pyautogui.scroll(scroll_amount)
            elif event[0] == "key":
                if event[1] is not None:
                    pyautogui.press(event[1])
            elif event[0] == "key_special":
                key_name = event[1].replace("Key.", "").lower()
                try:
                    pyautogui.press(key_name)
                except:
                    pass  # Skip keys that pyautogui doesn't recognize

        if playing and i < repeat - 1:
            time.sleep(gap)

    playing = False
    print("\n[■] Playback finished.")
    return repeat  # All iterations completed


def main():
    global recording, playing, play_thread, events, current_recording_name

    # Check for existing recordings
    existing = list_recordings()
    if existing:
        print("\n[📂] Existing recordings found:")
        for idx, name in enumerate(existing, 1):
            print(f"  {idx}. {name}")
        print("\n[Options]")
        print("  1. Load existing recording")
        print("  2. Create new recording")
        choice = input("\nYour choice (1/2): ").strip()
        
        if choice == "1":
            rec_num = int(input(f"Enter recording number (1-{len(existing)}): ")) - 1
            if 0 <= rec_num < len(existing):
                current_recording_name = existing[rec_num]
                events = load_recording_from_csv(current_recording_name)
                if events is None:
                    print("[!] Failed to load recording. Exiting.")
                    return
            else:
                print("[!] Invalid selection. Exiting.")
                return
        else:
            current_recording_name = input("\nEnter name for new recording: ").strip()
            if not current_recording_name:
                current_recording_name = f"recording_{int(time.time())}"
            
            print(f"\n[Hotkeys]")
            print("  Ctrl+Alt+R → Stop recording")
            print("\nRecording started... (press Ctrl+Alt+R to stop)")

            record_thread = threading.Thread(target=record_mouse, daemon=True)
            record_thread.start()

            keyboard.wait("ctrl+alt+r")
            recording = False
            record_thread.join()

            if not events:
                print("[!] No events recorded. Exiting.")
                return
            
            save_recording_to_csv(current_recording_name, events)
    else:
        current_recording_name = input("\nEnter name for new recording: ").strip()
        if not current_recording_name:
            current_recording_name = f"recording_{int(time.time())}"
        
        print(f"\n[Hotkeys]")
        print("  Ctrl+Alt+R → Stop recording")
        print("\nRecording started... (press Ctrl+Alt+R to stop)")

        record_thread = threading.Thread(target=record_mouse, daemon=True)
        record_thread.start()

        keyboard.wait("ctrl+alt+r")
        recording = False
        record_thread.join()

        if not events:
            print("[!] No events recorded. Exiting.")
            return
        
        save_recording_to_csv(current_recording_name, events)

    repeat = int(input("\nHow many times should the auto clicker run? "))
    gap = float(input("Gap between consecutive runs (seconds)? "))

    print("\n[Hotkeys]")
    print("  Ctrl+Alt+P → Start/Pause playback")
    print("  Ctrl+Alt+R → Record new/overwrite")
    print("\nPress Ctrl+Alt+P to START playback...")
    keyboard.wait("ctrl+alt+p")
    time.sleep(0.3)  # Debounce
    
    completed_runs = 0
    while completed_runs < repeat:
        remaining = repeat - completed_runs
        print(f"[▶] Playing... {remaining} runs remaining (Ctrl+Alt+P=pause, Ctrl+Alt+R=new recording)")
        play_thread = threading.Thread(target=play_events, args=(remaining, gap), daemon=True)
        play_thread.start()

        last_press_p = 0
        last_press_r = 0
        while play_thread.is_alive():
            if keyboard.is_pressed("ctrl+alt+p"):
                current_time = time.time()
                if current_time - last_press_p > 0.5:  # Debounce 500ms
                    last_press_p = current_time
                    playing = False
                    print("\n[■] Playback paused.")
                    time.sleep(0.3)  # Wait for key release
                    break
            elif keyboard.is_pressed("ctrl+alt+r"):
                current_time = time.time()
                if current_time - last_press_r > 0.5:  # Debounce 500ms
                    last_press_r = current_time
                    playing = False
                    print("\n[⏸] Playback stopped for new recording.")
                    time.sleep(0.3)
                    
                    print("\n[Options]")
                    print("  1. Record new (keep current)")
                    print("  2. Overwrite current recording")
                    rec_choice = input("Your choice (1/2): ").strip()
                    
                    if rec_choice == "2":
                        new_name = current_recording_name
                    else:
                        new_name = input("Enter name for new recording: ").strip()
                        if not new_name:
                            new_name = f"recording_{int(time.time())}"
                    
                    print(f"\nRecording '{new_name}'... (press Ctrl+Alt+R to stop)")
                    record_thread = threading.Thread(target=record_mouse, daemon=True)
                    record_thread.start()
                    keyboard.wait("ctrl+alt+r")
                    recording = False
                    record_thread.join()
                    
                    if events:
                        save_recording_to_csv(new_name, events)
                        current_recording_name = new_name
                        print("\n[Options]")
                        print("  1. Continue with old playback")
                        print("  2. Start new playback with new recording")
                        continue_choice = input("Your choice (1/2): ").strip()
                        
                        if continue_choice == "2":
                            repeat = int(input("\nHow many times should the auto clicker run? "))
                            gap = float(input("Gap between consecutive runs (seconds)? "))
                            completed_runs = 0
                            print("\nPress Ctrl+Alt+P to START playback...")
                            keyboard.wait("ctrl+alt+p")
                            time.sleep(0.3)
                            continue
                    break
            time.sleep(0.05)

        play_thread.join()
        
        if play_thread is not None:
            completed_runs = repeat - remaining + (0 if playing else 0)
        
        if not playing and completed_runs < repeat:
            print(f"\nPress Ctrl+Alt+P to RESUME playback... ({repeat - completed_runs} runs left)")
            keyboard.wait("ctrl+alt+p")
            time.sleep(0.3)  # Debounce
        else:
            break

    print("\n[✓] All runs completed!")


if __name__ == "__main__":
    main()
