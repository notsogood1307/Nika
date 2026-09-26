import re

error_msg = r"""Something went wrong processing a tool call: Error code: 400 - {'error': {'message': "Failed to call a function. Please adjust your prompt. See 'failed_generation' for more details.", 'type': 'invalid_request_error', 'code': 'tool_use_failed', 'failed_generation': '<tool_call>\n<function=open_app>\n<parameter=name>\nbrowser\n</parameter>\n</function>\n articol'}}"""

func_name_match = re.search(r"<function=(\w+)>", error_msg)
if func_name_match:
    func_name = func_name_match.group(1)
    params = {}
    # Groq's failed generation uses <parameter=name>value</parameter>
    # Note that in the repr string it has \n. We should handle both actual newlines and literal '\n'
    # Wait, the string above has literal \n in failed_generation: '<tool_call>\\n<function=open_app>\\n...'
    param_matches = re.finditer(r"<parameter=(\w+)>\\?n?(.*?)\\?n?</parameter>", error_msg)
    for pm in param_matches:
        val = pm.group(2).strip()
        params[pm.group(1)] = val
    
    print(f"Salvaged: {func_name}({params})")
else:
    print("No function match found.")
