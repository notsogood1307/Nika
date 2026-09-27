import os
import subprocess
import time
import webbrowser
import pyautogui
import guardrails
import logging
import pygetwindow as gw
import threading
import screen_capture
import grounding

APP_WHITELIST = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "browser": "start http://"
}

last_target_window_title = None

def _track_window():
    global last_target_window_title
    while True:
        time.sleep(0.5)
        if guardrails.kill_switch_active:
            continue
        try:
            win = gw.getActiveWindow()
            if win and win.title:
                title = win.title
                title_lower = title.lower()
                if not any(x in title_lower for x in ["nika", "cmd", "powershell", "python"]):
                    last_target_window_title = title
        except Exception:
            pass

threading.Thread(target=_track_window, daemon=True).start()

def _re_activate_window():
    global last_target_window_title
    if not last_target_window_title:
        return False
    try:
        windows = gw.getWindowsWithTitle(last_target_window_title)
        if windows:
            win = windows[0]
            if not win.isActive:
                win.activate()
            time.sleep(0.2)
            return True
    except Exception:
        pass
    return False

def check_kill_switch():
    if guardrails.kill_switch_active:
        return True
    return False

def open_app(name: str) -> str:
    if check_kill_switch():
        return "Action cancelled by kill switch."
    
    name_lower = name.lower()
    if name_lower not in APP_WHITELIST:
        return f"I don't have '{name}' in my approved app list."
        
    cmd = APP_WHITELIST[name_lower]
    try:
        if cmd.startswith("start "):
            os.system(cmd)
        else:
            subprocess.Popen(cmd)
            
        time.sleep(1.5)
        try:
            win = gw.getActiveWindow()
            if win and win.title:
                global last_target_window_title
                last_target_window_title = win.title
        except Exception:
            pass
            
        return f"Opened {name.capitalize()}."
    except Exception as e:
        return f"Failed to open {name}: {e}"

def type_text(text: str) -> str:
    if check_kill_switch():
        return "Action cancelled by kill switch."
        
    if not _re_activate_window():
        return "I couldn't confirm the right window was focused before typing — please check where the text landed."
        
    time.sleep(0.3)
    if check_kill_switch():
        return "Action cancelled by kill switch."
        
    try:
        pyautogui.write(text)
        return f"Typed: '{text}'"
    except Exception as e:
        return f"Failed to type text: {e}"

def press_key(key: str) -> str:
    if check_kill_switch():
        return "Action cancelled by kill switch."
        
    if not _re_activate_window():
        return "I couldn't confirm the right window was focused before typing — please check where the text landed."
        
    try:
        keys = key.split("+")
        if len(keys) > 1:
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(key)
        return f"Pressed key(s): {key}"
    except Exception as e:
        return f"Failed to press key: {e}"

def open_url(url: str) -> str:
    if check_kill_switch():
        return "Action cancelled by kill switch."
        
    try:
        webbrowser.open(url)
        return f"Opened URL: {url}"
    except Exception as e:
        return f"Failed to open URL: {e}"

def click_element(description: str) -> str:
    if check_kill_switch():
        return "Action cancelled by kill switch."
        
    try:
        # Capture screen with metadata to calculate absolute coordinates
        image, offset_left, offset_top, width, height = screen_capture.capture_screen_with_metadata()
        
        # Find the click target using vision grounding
        target = grounding.find_click_target(image, description)
        if not target:
            return f"I couldn't find '{description}' on your screen."
            
        pixel_x, pixel_y = target
        
        # Convert screenshot-relative pixel coordinates to absolute screen coordinates
        absolute_x = pixel_x + offset_left
        absolute_y = pixel_y + offset_top
        
        logging.debug(f"Computed absolute coordinates for '{description}': ({absolute_x}, {absolute_y})")
        
        # Final kill switch check right before clicking
        if check_kill_switch():
            return "Action cancelled by kill switch."
            
        pyautogui.click(absolute_x, absolute_y)
        return f"Clicked '{description}' at ({absolute_x}, {absolute_y})."
    except Exception as e:
        return f"Failed to click element: {e}"
