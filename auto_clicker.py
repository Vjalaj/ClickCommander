import time
import threading
import keyboard
import pyautogui
from pynput import mouse, keyboard as pynkey

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0  # Remove default pause between pyautogui actions

events = []
recording = False
playing = False
start_time = None
play_thread = None


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
    global recording, playing, play_thread

    repeat = int(input("How many times should the auto clicker run? "))
    gap = float(input("Gap between consecutive runs (seconds)? "))

    print("\n[Hotkeys]")
    print("  Ctrl+Alt+R → Stop recording")
    print("  Ctrl+Alt+P → Start/Stop playback")
    print("\nRecording started... (press Ctrl+Alt+R to stop)")

    record_thread = threading.Thread(target=record_mouse, daemon=True)
    record_thread.start()

    keyboard.wait("ctrl+alt+r")
    recording = False
    record_thread.join()

    if not events:
        print("[!] No events recorded. Exiting.")
        return

    print("\nPress Ctrl+Alt+P to START playback...")
    keyboard.wait("ctrl+alt+p")
    time.sleep(0.3)  # Debounce
    
    completed_runs = 0
    while completed_runs < repeat:
        remaining = repeat - completed_runs
        print(f"[▶] Playing... {remaining} runs remaining (press Ctrl+Alt+P to pause)")
        play_thread = threading.Thread(target=play_events, args=(remaining, gap), daemon=True)
        play_thread.start()

        last_press = 0
        while play_thread.is_alive():
            if keyboard.is_pressed("ctrl+alt+p"):
                current_time = time.time()
                if current_time - last_press > 0.5:  # Debounce 500ms
                    last_press = current_time
                    playing = False
                    print("\n[■] Playback paused.")
                    time.sleep(0.3)  # Wait for key release
                    break
            time.sleep(0.05)

        play_thread.join()
        
        if play_thread is not None:
            # Get completed runs from thread (stored in a simple way)
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
