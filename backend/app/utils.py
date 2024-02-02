def format_prompt_payload(prompt_payload):
    prompt_string = prompt_payload['template']
    for prompt_key, prompt_value in prompt_payload.items():
        if prompt_key != "template":
            prompt_string = prompt_string.replace("{" + prompt_key + "}", prompt_value)
    return prompt_string