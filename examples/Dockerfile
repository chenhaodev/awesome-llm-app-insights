# Use an alias for the base image for easier updates
FROM python:3.10 as base

# Set model
ENV MODEL=Qwen/Qwen1.5-14B-Chat-GGUF
ENV QUANT=Q5_K_M
ENV CHAT_TEMPLATE=llama-2

# Set the working directory
WORKDIR /app

# Install Python requirements
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Download model
RUN MODEL_NAME_FILE=$(echo ${MODEL#*/} | tr '[:upper:]' '[:lower:]' | sed 's/-gguf$//') && \
    wget https://huggingface.co/Qwen/Qwen1.5-14B-Chat-GGUF/resolve/main/qwen1_5-14b-chat-q5_k_m.gguf -O model.gguf

# Copy the rest of your application
COPY . .

# Command to run the application
CMD ["python", "app.py"]
