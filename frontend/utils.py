import os
import json
import yaml

def retrieve_prompt_templates():
    filepaths = os.listdir("./prompts")
    return [
        (os.path.basename(filepath).split(".")[0], os.path.join("./prompts", filepath))
        for filepath in filepaths
    ]

def load_config_yaml(filepath):
    try:
        with open(filepath, "r") as yaml_file:
            return yaml.load(yaml_file)
    except yaml.YamlError as err:
        raise ValueError(
            "Invalid yaml filepath specified!"
        ) from err

def save_contents_to_json(content, filepath):
    with open(filepath, "w") as save_file:
        json.dump(save_file, content)

def open_contents_from_json(filepath):
    with open(filepath, "r") as open_file:
        return json.load(open_file)


def convert_prompt_template_into_prompt_payload(user_prompt, prompt_template):
    prompt_template['user'] = user_prompt
    return prompt_template