import time
import threading
import keyboard
import pyautogui
import csv
import os
import math
from datetime import datetime, timedelta
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

    def on_key_release(key):
        if not recording:
            return False
        t = time.time() - start_time
        try:
            events.append(("key_release", key.char, t))
        except AttributeError:
            events.append(("key_release_special", str(key), t))

    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    key_listener = pynkey.Listener(on_press=on_key_press, on_release=on_key_release)
    
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
            # Pad all events to 6 fields for consistency
            event_type = event[0]
            if event_type in ["move", "drag"]:
                # (type, x, y, timestamp) -> pad with empty strings
                writer.writerow([event[0], event[1], event[2], "", "", event[3]])
            elif event_type in ["press", "release"]:
                # (type, x, y, button, timestamp) -> pad with one empty string
                writer.writerow([event[0], event[1], event[2], event[3], "", event[4]])
            elif event_type == "scroll":
                # (type, x, y, amount, timestamp) -> pad with one empty string
                writer.writerow([event[0], event[1], event[2], event[3], "", event[4]])
            elif event_type == "key":
                # (type, char, timestamp) -> pad with empty strings
                writer.writerow([event[0], event[1], "", "", "", event[2]])
            elif event_type == "key_special":
                # (type, key_name, timestamp) -> pad with empty strings
                writer.writerow([event[0], event[1], "", "", "", event[2]])
            elif event_type == "key_release":
                # (type, char, timestamp) -> pad with empty strings
                writer.writerow([event[0], event[1], "", "", "", event[2]])
            elif event_type == "key_release_special":
                # (type, key_name, timestamp) -> pad with empty strings
                writer.writerow([event[0], event[1], "", "", "", event[2]])
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
            if not row or len(row) < 6:  # Skip invalid rows
                continue
            # All rows now have 6 fields, timestamp is always at index 5
            event_type = row[0]
            if event_type in ["move", "drag"]:
                events_list.append((event_type, int(row[1]), int(row[2]), float(row[5])))
            elif event_type in ["press", "release"]:
                events_list.append((event_type, int(row[1]), int(row[2]), row[3], float(row[5])))
            elif event_type == "scroll":
                events_list.append((event_type, int(row[1]), int(row[2]), int(row[3]), float(row[5])))
            elif event_type == "key":
                events_list.append((event_type, row[1] if row[1] and row[1] != "" else None, float(row[5])))
            elif event_type == "key_special":
                events_list.append((event_type, row[1], float(row[5])))
            elif event_type == "key_release":
                events_list.append((event_type, row[1] if row[1] and row[1] != "" else None, float(row[5])))
            elif event_type == "key_release_special":
                events_list.append((event_type, row[1], float(row[5])))
    
    print(f"[📂] Recording loaded from {filepath}")
    return events_list


def list_recordings():
    """List all saved recordings"""
    if not os.path.exists(RECORDINGS_DIR):
        return []
    
    files = [f[:-4] for f in os.listdir(RECORDINGS_DIR) if f.endswith('.csv')]
    return files


def parse_time_input(time_str):
    """Parse a user-provided time string and return a datetime for scheduling.
    Accepted examples: '08:00', '8:00 am', '2026-04-15 08:00', '08:00:00'.
    If a date is not provided, the time is scheduled for today or tomorrow
    (tomorrow if the time today already passed).
    Returns None if parsing fails.
    """
    if not time_str:
        return None
    time_str = time_str.strip()
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %I:%M %p",
        "%Y-%m-%d %I:%M:%S %p",
        "%H:%M:%S",
        "%H:%M",
        "%I:%M %p",
        "%I:%M:%S %p",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(time_str, fmt)
            # If parsed value did not include a year, assign today's date
            if "%Y" not in fmt:
                now = datetime.now()
                dt = dt.replace(year=now.year, month=now.month, day=now.day)
                if dt <= now:
                    dt = dt + timedelta(days=1)
            return dt
        except ValueError:
            continue
    return None


def move_smooth_to(x, y, speed=800, min_duration=0.02, initial_slow_fraction=0.15):
    """Move the mouse from current position to (x, y) smoothly.

    - `speed` is pixels per second used to compute duration (larger = faster).
    - If the distance is large, first move a small fraction slowly to avoid
      abrupt jumps, then finish the move.
    - Always reads the current mouse position, so it adapts if the user moved
      the mouse between recorded events.
    """
    try:
        cur_x, cur_y = pyautogui.position()
    except Exception:
        # Fallback: if position can't be read, just teleport
        try:
            pyautogui.moveTo(x, y)
        except Exception:
            pass
        return

    dx = x - cur_x
    dy = y - cur_y
    distance = math.hypot(dx, dy)
    if distance <= 1:
        return

    # Duration based on speed (pixels/sec)
    duration = max(min_duration, distance / float(max(1, speed)))

    # If movement is large, do an initial slow nudge
    try:
        if distance > 30:
            nx = int(cur_x + dx * initial_slow_fraction)
            ny = int(cur_y + dy * initial_slow_fraction)
            initial_duration = max(min_duration, (distance * initial_slow_fraction) / float(max(1, speed * 0.35)))
            pyautogui.moveTo(nx, ny, duration=initial_duration)

        pyautogui.moveTo(x, y, duration=duration)
    except Exception:
        try:
            pyautogui.moveTo(x, y)
        except Exception:
            pass


def get_playback_settings_and_wait():
    """Prompt for repeat/gap/schedule/start-delay/stop-after and wait until start time or hotkey press.

    Returns (repeat, gap, stop_after_seconds).
    """
    repeat = int(input("\nHow many times should the auto clicker run? "))
    gap_input = input("Gap between consecutive runs (seconds)? ").strip()
    gap = 0 if gap_input == "" else float(gap_input)

    schedule_input = input(
        "\nSchedule start time (e.g., '08:00', '8:00 am', or '2026-04-15 08:00') (leave blank to use start-delay or start manually): "
    ).strip()

    start_delay_input = input("Start after how many seconds? (leave blank to ignore): ").strip()
    stop_after_input = input("Stop after how many seconds? (leave blank to stop by repeat): ").strip()

    scheduled_dt = None
    if schedule_input:
        scheduled_dt = parse_time_input(schedule_input)
        if scheduled_dt is None:
            print("[!] Could not parse time. Accepted formats: HH:MM, H:MM AM/PM, YYYY-MM-DD HH:MM")
            scheduled_dt = None
    elif start_delay_input:
        try:
            sdelay = float(start_delay_input)
            if sdelay > 0:
                scheduled_dt = datetime.now() + timedelta(seconds=sdelay)
                print(f"[⏳] Will start in {int(sdelay)} seconds at {scheduled_dt.strftime('%Y-%m-%d %H:%M:%S')}.")
            else:
                scheduled_dt = None
        except Exception:
            print("[!] Invalid start delay. Start manually.")
            scheduled_dt = None

    print("\n[Hotkeys]")
    print("  Ctrl+Alt+P → Start/Pause playback")
    print("  Ctrl+Alt+R → Record new/overwrite")

    if scheduled_dt:
        now = datetime.now()
        remaining = (scheduled_dt - now).total_seconds()
        if remaining > 0:
            try:
                # Show a live countdown (update every second)
                while True:
                    remaining = (scheduled_dt - datetime.now()).total_seconds()
                    if remaining <= 0:
                        # Clear the line then break
                        print("\r" + " " * 120, end="\r", flush=True)
                        break
                    secs = int(remaining)
                    hrs, rem = divmod(secs, 3600)
                    mins, secs = divmod(rem, 60)
                    if hrs > 0:
                        time_str = f"{hrs}h {mins}m {secs}s"
                    elif mins > 0:
                        time_str = f"{mins}m {secs}s"
                    else:
                        time_str = f"{secs}s"
                    print(f"\r[⏳] Scheduled for {scheduled_dt.strftime('%Y-%m-%d %H:%M:%S')} (in {time_str})", end="", flush=True)
                    time.sleep(1)
                print()
            except KeyboardInterrupt:
                print("\n[!] Waiting canceled by user. Start manually.")
                scheduled_dt = None
        else:
            print("[!] Target time appears to be in the past. Start manually.")
            scheduled_dt = None

    if scheduled_dt:
        print("\n[▶] Scheduled time reached — starting playback automatically.")
        time.sleep(0.5)
    else:
        print("\nPress Ctrl+Alt+P to START playback...")
        keyboard.wait("ctrl+alt+p")
        time.sleep(0.5)  # Longer debounce to ensure key is released

    stop_after_seconds = None
    if stop_after_input:
        try:
            stop_after_seconds = float(stop_after_input)
            if stop_after_seconds <= 0:
                stop_after_seconds = None
        except Exception:
            stop_after_seconds = None

    return repeat, gap, stop_after_seconds


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
                move_smooth_to(event[1], event[2])
            elif event[0] == "drag":
                # Keep mouse button state from press/release events; move will drag
                move_smooth_to(event[1], event[2])
            elif event[0] == "press":
                btn = event[3]
                move_smooth_to(event[1], event[2])
                if btn == "left":
                    pyautogui.mouseDown(button="left")
                elif btn == "right":
                    pyautogui.mouseDown(button="right")
                elif btn == "middle":
                    pyautogui.mouseDown(button="middle")
            elif event[0] == "release":
                btn = event[3]
                move_smooth_to(event[1], event[2])
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
                    pyautogui.keyDown(event[1])
            elif event[0] == "key_special":
                key_name = event[1].replace("Key.", "").lower()
                try:
                    pyautogui.keyDown(key_name)
                except:
                    pass
            elif event[0] == "key_release":
                if event[1] is not None:
                    pyautogui.keyUp(event[1])
            elif event[0] == "key_release_special":
                key_name = event[1].replace("Key.", "").lower()
                try:
                    pyautogui.keyUp(key_name)
                except:
                    pass

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

    repeat, gap, stop_after = get_playback_settings_and_wait()

    completed_runs = 0
    timed_out = False
    while completed_runs < repeat:
        remaining = repeat - completed_runs
        print(f"[▶] Playing... {remaining} runs remaining (Ctrl+Alt+P=pause, Ctrl+Alt+R=new recording)")
        play_thread = threading.Thread(target=play_events, args=(remaining, gap), daemon=True)
        play_thread.start()

        # Track playback start time for optional automatic stop-after timeout
        play_start_time = time.time()
        end_time = play_start_time + stop_after if (stop_after is not None) else None

        last_press_p = time.time()  # Initialize with current time to prevent immediate trigger
        last_press_r = time.time()
        while play_thread.is_alive():
            # Check for automatic timeout
            if end_time is not None and time.time() >= end_time:
                playing = False
                timed_out = True
                print("\n[⏱] Stop-after timeout reached — stopping playback.")
                time.sleep(0.3)
                break
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
                            repeat, gap, stop_after = get_playback_settings_and_wait()
                            completed_runs = 0
                            continue
                    break
            time.sleep(0.05)

        play_thread.join()

        if timed_out:
            # stop completely if we hit the stop-after timeout
            completed_runs = repeat
            break

        if play_thread is not None:
            completed_runs = repeat - remaining + (0 if playing else 0)
        
        if not playing and completed_runs < repeat:
            print(f"\nPress Ctrl+Alt+P to RESUME playback... ({repeat - completed_runs} runs left)")
            print("Or press Ctrl+Alt+R to record new/overwrite")
            
            # Wait for either P or R
            while True:
                if keyboard.is_pressed("ctrl+alt+p"):
                    time.sleep(0.5)
                    break
                elif keyboard.is_pressed("ctrl+alt+r"):
                    time.sleep(0.5)
                    
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
                            repeat, gap, stop_after = get_playback_settings_and_wait()
                            completed_runs = 0
                            break
                        else:
                            # Continue with old playback
                            print("\nPress Ctrl+Alt+P to RESUME playback...")
                            keyboard.wait("ctrl+alt+p")
                            time.sleep(0.5)
                            break
                    else:
                        # No events recorded, go back to waiting
                        print(f"\nPress Ctrl+Alt+P to RESUME playback... ({repeat - completed_runs} runs left)")
                        continue
                time.sleep(0.1)
        else:
            break

    print("\n[✓] All runs completed!")


if __name__ == "__main__":
    main()