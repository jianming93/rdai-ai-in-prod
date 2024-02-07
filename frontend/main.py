import gradio as gr
import os
import time
import logging

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s", level=logging.INFO
)
import json
import requests

from utils import (
    retrieve_prompt_templates,
    open_contents_from_json,
    save_contents_to_json,
    convert_prompt_template_into_prompt_payload,
)

SLEEP_TIMING = 0.01
PROMPTS = retrieve_prompt_templates()


def slow_echo(message, history, prompt_template_filepath):
    # Post the message to backend
    prompt_template = open_contents_from_json(prompt_template_filepath)
    prompt_payload = convert_prompt_template_into_prompt_payload(
        message, prompt_template
    )
    response = requests.post(
        f'{os.environ["BACKEND_URL"]}:{os.environ["BACKEND_PORT"]}{os.environ["BACKEND_PROMPT_PATH"]}',
        json=prompt_payload,
    )
    json_response = response.json()
    for i in range(len(json_response["result"])):
        time.sleep(SLEEP_TIMING)
        yield json_response["result"][: i + 1]


def reload_prompt_contents(filepath):
    new_prompt_contents = open_contents_from_json(filepath)
    return json.dumps(new_prompt_contents)


def show_info_for_create_new(content, filename):
    global PROMPTS
    filepath = f"./prompts/{filename}.json"
    save_contents_to_json(json.loads(content), filepath)
    gr.Info("Successfully saved!")
    PROMPTS = retrieve_prompt_templates()
    return (
        gr.Dropdown(
            choices=PROMPTS,
            value=PROMPTS[0][1],
            label="Prompt Templates",
            info="Select prompt template to edit.",
            interactive=True,
        ),
        gr.Dropdown(
            choices=PROMPTS,
            value=PROMPTS[0][1],
            label="Prompt Template",
            info="Select prompt template to use.",
            interactive=True,
        ),
        gr.Dropdown(
            choices=PROMPTS,
            value=PROMPTS[0][1],
            label="Prompt Template",
            info="Select prompt template to view.",
            interactive=True,
        ),
    )


def show_info_for_edit_existing(content, filepath):
    global PROMPTS
    save_contents_to_json(json.loads(content), filepath)
    gr.Info("Successfully saved!")
    PROMPTS = retrieve_prompt_templates()
    for i in range(len(PROMPTS)):
        if PROMPTS[i][1] == filepath:
            index = i
            break
    return existing_prompt_editor, gr.Dropdown(
        choices=PROMPTS,
        value=PROMPTS[index][1],
        label="Prompt Templates",
        info="Select prompt template to edit.",
        interactive=True,
    )


################
# Chatbot page #
################
with gr.Blocks(title="RAG Chatbot") as CHAT_PAGE:
    chat_summary_markdown = gr.Markdown(
        "Hi, I am a chatbot. Please feel free to ask me anything."
    )
    with gr.Tab("Chatbot") as chatbot:
        prompts_select_dropdown = gr.Dropdown(
            choices=PROMPTS,
            value=PROMPTS[0][1],
            label="Prompt Template",
            info="Select prompt template to use.",
            interactive=True,
        )
        # Create chat interface
        chatbot = gr.ChatInterface(
            slow_echo, title="Chatbot", additional_inputs=[prompts_select_dropdown]
        )
    with gr.Tab("Prompt Viewer") as prompt_viewer:
        with gr.Row() as prompt_viewer_tab:
            with gr.Column(scale=1) as prompt_viewer_dropdown_column:
                prompt_viewer_dropdown = gr.Dropdown(
                    choices=PROMPTS,
                    value=PROMPTS[0][1],
                    label="Prompt Template",
                    info="Select prompt template to view.",
                    interactive=True,
                )
            with gr.Column(scale=3) as prompt_viewer_contents_column:
                prompt_json_display = gr.JSON(
                    open_contents_from_json(PROMPTS[0][1]),
                    label="Prompt Contents",
                )
#######################
# Prompt Creator page #
#######################
with gr.Blocks(title="Prompt Creator") as PROMPT_CREATOR_PAGE:
    with gr.Tab("Create New Prompt") as create_new_prompt_tab:
        create_new_prompt_summary_markdown = gr.Markdown(
            "Create your own prompts in json format."
        )
        new_prompt_editor = gr.Code(
            value='{\n\t"config": {"temperature": "1.0", "top_p": "0.95", "max_tokens": "256"},\n\t"system": "",\n\t"user": "",\n\t"template": "{system}{user}"\n}',
            language="json",
            label="Prompt JSON",
            interactive=True,
        )
        filename_input = gr.Textbox(label="Filename")
        save_new_prompt_button = gr.Button("Save")

    with gr.Tab("Edit Existing Prompt") as edit_existing_prompt_tab:
        edit_existing_prompt_summary_markdown = gr.Markdown(
            "Edit current prompts in json format."
        )
        with gr.Row() as editor_container:
            with gr.Column(scale=1) as prompt_dropdown_column:
                prompt_dropdown = gr.Dropdown(
                    choices=PROMPTS,
                    value=PROMPTS[0][1],
                    label="Prompt Templates",
                    info="Select prompt template to edit.",
                    interactive=True,
                )
            with gr.Column(scale=3) as prompt_editor_column:
                existing_prompt_editor = gr.Code(
                    value=json.dumps(open_contents_from_json(prompt_dropdown.value)),
                    language="json",
                    label="Prompt JSON",
                    interactive=True,
                )
                save_edited_prompt_button = gr.Button("Save")
    # Events
    prompt_viewer_dropdown.input(
        open_contents_from_json,
        inputs=[prompt_viewer_dropdown],
        outputs=[prompt_json_display],
    )
    save_new_prompt_button.click(
        show_info_for_create_new,
        inputs=[new_prompt_editor, filename_input],
        outputs=[prompt_dropdown, prompts_select_dropdown, prompt_viewer_dropdown],
    )
    save_edited_prompt_button.click(
        show_info_for_edit_existing,
        inputs=[existing_prompt_editor, prompt_dropdown],
        outputs=[existing_prompt_editor, prompt_dropdown],
    )
    prompt_dropdown.input(
        reload_prompt_contents,
        inputs=[prompt_dropdown],
        outputs=[existing_prompt_editor],
        api_name="load_another_prompt",
    )


if __name__ == "__main__":
    gr.TabbedInterface(
        [CHAT_PAGE, PROMPT_CREATOR_PAGE], tab_names=["Chatbot", "Prompt Creator"]
    ).launch(share=False, server_name="0.0.0.0", server_port=7070)
