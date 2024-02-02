import gradio as gr
import json
import logging
logging.basicConfig(
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    level=logging.INFO
)
from utils import retrieve_prompt_templates, open_contents_from_json

def reload_prompt_contents(filepath):
    new_prompt_contents = open_contents_from_json(filepath)
    return json.dumps(new_prompt_contents)

with gr.Blocks(title="Prompt Creator") as PROMPT_CREATOR_PAGE:
    prompts = retrieve_prompt_templates()
    with gr.Tab("Create New Prompt") as create_new_prompt_tab:
        create_new_prompt_summary_markdown = gr.Markdown("Create your own prompts in json format.")
        new_prompt_editor = gr.Code(value="{\n\n}", language="json", label="Prompt JSON", interactive=True)
        filename_input = gr.Textbox(label="Filename")
        save_button = gr.Button("Save")
    with gr.Tab("Edit Existing Prompt") as edit_existing_prompt_tab:
        edit_existing_prompt_summary_markdown = gr.Markdown("Edit current prompts in json format.")
        with gr.Row() as editor_container:
            with gr.Column(scale=1) as prompt_dropdown_column:
                prompt_dropdown = gr.Dropdown(
                    choices=prompts,
                    value=prompts[0][1],
                    label="Prompt Templates",
                    info="Select prompt template to edit.",
                    interactive=True,
                )
            with gr.Column(scale=3) as prompt_editor_column:
                loaded_prompt = open_contents_from_json(prompt_dropdown.value)
                existing_prompt_editor = gr.Code(value=json.dumps(loaded_prompt), language="json", label="Prompt JSON", interactive=True)
                save_edited_prompt_button = gr.Button("Save")
            prompt_dropdown.input(reload_prompt_contents, inputs=[prompt_dropdown], outputs=[existing_prompt_editor], api_name="load_another_prompt")
