import gradio as gr
import json
import logging
logging.basicConfig(
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    level=logging.INFO
)
from utils import retrieve_prompt_templates, open_contents_from_json, save_contents_to_json

def reload_prompt_contents(filepath):
    new_prompt_contents = open_contents_from_json(filepath)
    return json.dumps(new_prompt_contents)

def show_info_for_create_new(content, filename):
    save_contents_to_json(json.dumps(content), f'./prompt/{filename}.json')
    gr.Info("Successfully saved!", css='{background-color: #3eb55d}')

def show_info_for_edit_existing(content, filepath):
    save_contents_to_json(json.dumps(content), filepath)
    gr.Info("Successfully saved!")

with gr.Blocks(title="Prompt Creator") as PROMPT_CREATOR_PAGE:
    prompts = retrieve_prompt_templates()
    with gr.Tab("Create New Prompt") as create_new_prompt_tab:
        create_new_prompt_summary_markdown = gr.Markdown("Create your own prompts in json format.")
        new_prompt_editor = gr.Code(value="{\n'config': {'temperature': '1.0', 'top_p': '0.95', 'max_tokens': '256'},\n'system': '',\n'user': '',\n'template': '{system}{user}'\n}", language="json", label="Prompt JSON", interactive=True)
        filename_input = gr.Textbox(label="Filename")
        save_button = gr.Button("Save")
        save_button.click(show_info_for_create_new, inputs=[new_prompt_editor, filename_input], outputs=None)
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
                save_edited_prompt_button.click(show_info_for_edit_existing, inputs=[existing_prompt_editor, prompt_dropdown], outputs=None)
            prompt_dropdown.input(reload_prompt_contents, inputs=[prompt_dropdown], outputs=[existing_prompt_editor], api_name="load_another_prompt")
