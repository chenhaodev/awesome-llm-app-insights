import os
import json
import gradio as gr
from llama_cpp import Llama

# Get environment variables
model_id = os.getenv('MODEL')
quant = os.getenv('QUANT')
chat_template = os.getenv('CHAT_TEMPLATE')

# Interface variables
model_name = model_id.split('/')[1].split('-GGUF')[0]
title = f"{model_name}"
description = f"Chat with <a href=\"https://huggingface.co/{model_id}\">{model_name}</a> in GGUF format ({quant})!"

# Initialize the LLM
llm = Llama(model_path="model.gguf",
            n_ctx=32768,
            n_threads=2,
            chat_format=chat_template)

# Function for streaming chat completions
def chat_stream_completion(message, history, system_prompt):
    messages_prompts = [{"role": "system", "content": system_prompt}]
    for human, assistant in history:
        messages_prompts.append({"role": "user", "content": human})
        messages_prompts.append({"role": "assistant", "content": assistant})
    messages_prompts.append({"role": "user", "content": message})

    response = llm.create_chat_completion(
        messages=messages_prompts,
        stream=True
    )
    message_repl = ""
    for chunk in response:
        if len(chunk['choices'][0]["delta"]) != 0 and "content" in chunk['choices'][0]["delta"]:
            message_repl = message_repl + chunk['choices'][0]["delta"]["content"]
        yield message_repl

# Gradio chat interface
gr.ChatInterface(
    fn=chat_stream_completion,
    title=title,
    description=description,
    additional_inputs=[gr.Textbox("You are helpful medical assistant.")],
    additional_inputs_accordion="System prompt",
    examples=[
        ["How to diagnose CHF?"],
        ["please write an extensive cancer patient story and case study for healthcare providers"],
        ["Also, please write journey how the cancer was discovered and what symptoms led to patient realization that something might be wrong."], 
        ["Additionally, please write up the intake scenario for her to be seen by a cancer specialist."]
    ]
).queue().launch(server_name="0.0.0.0")
