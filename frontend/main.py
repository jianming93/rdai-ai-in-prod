import gradio as gr

from pages.rag_chatbot import CHAT_PAGE
from pages.prompt_creator import PROMPT_CREATOR_PAGE


if __name__=="__main__":
    gr.TabbedInterface([CHAT_PAGE, PROMPT_CREATOR_PAGE], tab_names=["RAG Chatbot", "Prompt Creator"]).launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7070
    )