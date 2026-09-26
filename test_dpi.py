import mss
import ctypes
import sys

print("Before DPI awareness:")
with mss.mss() as sct:
    for idx, monitor in enumerate(sct.monitors[1:], start=1):
        print(f"Monitor {idx}: {monitor['width']}x{monitor['height']}")

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
    print("\nSetProcessDpiAwareness(2) called.")
except Exception as e:
    print("Failed to set DPI awareness via shcore:", e)
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        print("SetProcessDPIAware() called.")
    except Exception as e:
        print("Failed to set DPI awareness via user32:", e)

print("\nAfter DPI awareness:")
with mss.mss() as sct:
    for idx, monitor in enumerate(sct.monitors[1:], start=1):
        print(f"Monitor {idx}: {monitor['width']}x{monitor['height']}")
