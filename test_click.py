import os
import time
import actions

print("Starting Notepad...")
os.system("start notepad.exe")
time.sleep(2)

print("Attempting to click 'the File menu'...")
result = actions.click_element("the File menu")
print("Result:", result)
