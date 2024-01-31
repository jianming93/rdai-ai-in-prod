import os
import time
import gradio as gr
import logging
logging.basicConfig(
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    level=logging.INFO
)
import requests

from utils import retrieve_prompt_templates, open_contents_from_json, convert_prompt_template_into_prompt_payload

SLEEP_TIMING = 0.1

def slow_echo(message, history, prompt_template_filepath):
    # Post the message to backend
    prompt_template = open_contents_from_json(prompt_template_filepath)
    logging.info(prompt_template)
    prompt_payload = convert_prompt_template_into_prompt_payload(message, prompt_template)
    logging.info(prompt_payload)
    response = requests.post(
        f'{os.environ["BACKEND_URL"]}:{os.environ["BACKEND_PORT"]}{os.environ["BACKEND_PROMPT_PATH"]}',
        json=prompt_payload
    )
    for i in range(len(response)):
        time.sleep(SLEEP_TIMING)
        yield response[: i+1]

with gr.Blocks(title="RAG Chatbot") as CHAT_PAGE:
    chat_summary_markdown = gr.Markdown("Hi, I am a RAG demo chatbot for crypto content. Please feel free to ask me anything.")
    # Retrieve prompt templates and create dropdown
    prompts = retrieve_prompt_templates()
    with gr.Tab("Chatbot") as chatbot:
        prompts_select_dropdown = gr.Dropdown(
                choices=prompts,
                value=prompts[0][1],
                label="Prompt Template",
                info="Select prompt template to use.",
                interactive=True,
            )
        # Create chat interface
        chatbot = gr.ChatInterface(
            slow_echo,
            title="Chatbot",
            additional_inputs=[prompts_select_dropdown]
        )
    with gr.Tab("Prompt Viewer") as prompt_viewer:
        with gr.Row() as prompt_viewer_tab:
            with gr.Column(scale=1) as prompt_viewer_dropdown_column:
                prompt_viewer_dropdown = gr.Dropdown(
                    choices=prompts,
                    value=prompts[0][1],
                    label="Prompt Template",
                    info="Select prompt template to view.",
                    interactive=True,
                )
            with gr.Column(scale=3) as prompt_viewer_contents_column:
                prompt_json_display = gr.JSON(
                    open_contents_from_json(prompts[0][1]),
                    label="Prompt Contents",
                )
            prompt_viewer_dropdown.input(open_contents_from_json, inputs=[prompt_viewer_dropdown], outputs=[prompt_json_display])
