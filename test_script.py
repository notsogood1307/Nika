import time
import json
import brain
import actions
import pygetwindow as gw
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

def run_test():
    print("=== TEST 1: Open Notepad and Type ===")
    
    user_input = "Open Notepad and type 'Hello World'"
    print(f"User: {user_input}")
    
    intermediate = []
    
    # Run the loop just like main.py
    for _ in range(3):
        msg = brain.get_response_with_tools(user_input, "", [], intermediate)
        
        if getattr(msg, 'tool_calls', None) is None or not msg.tool_calls:
            print(f"Nika: {msg.content}")
            break
            
        msg_dict = {"role": "assistant", "content": msg.content}
        if msg.tool_calls:
            msg_dict["tool_calls"] = [{"id": tc.id, "type": tc.type, "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in msg.tool_calls]
        intermediate.append(msg_dict)
        
        for tc in msg.tool_calls:
            func_name = tc.function.name
            args = json.loads(tc.function.arguments)
            print(f"[Tool Call] Nika wants to run: {func_name}({args})")
            
            print("-> Mocking user confirmation delay (3 seconds)...")
            time.sleep(3)
            
            result = getattr(actions, func_name)(**args)
            print(f"-> Result: {result}")
            
            intermediate.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result)
            })

    print("\n=== TEST 2: Select all and delete ===")
    # Before test 2, ensure notepad is active to simulate user preparing the window
    print("-> Activating Notepad...")
    np = gw.getWindowsWithTitle("Notepad")
    if np:
        try:
            np[0].activate()
            time.sleep(1)
        except:
            pass

    user_input = "Select all the text and delete it"
    print(f"User: {user_input}")
    
    intermediate = []
    for _ in range(3):
        msg = brain.get_response_with_tools(user_input, "", [], intermediate)
        
        if getattr(msg, 'tool_calls', None) is None or not msg.tool_calls:
            print(f"Nika: {msg.content}")
            break
            
        msg_dict = {"role": "assistant", "content": msg.content}
        if msg.tool_calls:
            msg_dict["tool_calls"] = [{"id": tc.id, "type": tc.type, "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in msg.tool_calls]
        intermediate.append(msg_dict)
        
        for tc in msg.tool_calls:
            func_name = tc.function.name
            args = json.loads(tc.function.arguments)
            print(f"[Tool Call] Nika wants to run: {func_name}({args})")
            
            print("-> Mocking user confirmation delay (3 seconds)...")
            time.sleep(3)
            
            result = getattr(actions, func_name)(**args)
            print(f"-> Result: {result}")
            
            intermediate.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result)
            })
            
if __name__ == '__main__':
    run_test()
