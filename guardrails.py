import keyboard
import logging

kill_switch_active = False
session_approved = set()

RISK_TIERS = {
    "open_app": 1,
    "type_text": 2,
    "open_url": 3,
    "press_key": 3,
    "click_element": 3
}

def trigger_kill_switch():
    global kill_switch_active
    kill_switch_active = True
    print("\n[KILL SWITCH ACTIVATED] Halting any in-progress actions.")
    logging.info("[KILL SWITCH ACTIVATED]")

def register_kill_switch():
    keyboard.add_hotkey('ctrl+shift+esc', trigger_kill_switch)

def reset_kill_switch():
    global kill_switch_active
    kill_switch_active = False

def request_confirmation(action_name: str, args: dict, input_fn, print_fn, speak_fn) -> bool:
    tier = RISK_TIERS.get(action_name, 3)
    
    if tier == 1:
        return True
        
    if tier == 2 and action_name in session_approved:
        return True
        
    # Build prompt
    args_str = ", ".join([f"{k}='{v}'" for k, v in args.items()])
    
    if action_name == "click_element" and "description" in args:
        prompt_msg = f"I want to click on '{args['description']}' — ok? Say or type yes or no."
    elif tier == 2:
        prompt_msg = f"I want to {action_name} with ({args_str}) — ok? Say or type yes, no, or 'always allow' to skip asking again this session."
    else:
        prompt_msg = f"I want to {action_name} with ({args_str}) — ok? Say or type yes or no."
    
    print_fn(f"\n[Action Confirmation] {prompt_msg}")
    speak_fn(prompt_msg)
    
    # Strip whitespace and trailing punctuation often added by TTS
    reply = input_fn().lower().strip(" .!?")
    
    if reply in ['yes', 'y', 'ok', 'okay', 'sure', 'do it', 'allow']:
        return True
    elif reply in ['always allow', 'always', 'allow always']:
        if tier == 2:
            session_approved.add(action_name)
        return True
    
    return False
