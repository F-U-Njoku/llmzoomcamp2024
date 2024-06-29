FROM ollama/ollama:latest

# Set the working directory inside the container
WORKDIR /root/.ollama

# Copy the pre-pulled weights into the new image
COPY ./ollama_files /root/.ollama

# Ensure the weights directory has the correct permissions
RUN chmod -R 755 /root/.ollama