# Hugging Face Spaces runs this container. It only hosts the lightweight
# Streamlit + embedding layer — the LLM lives on your own machine.
FROM python:3.13.5-slim

WORKDIR /app

# build-essential is needed to compile some LlamaIndex/BM25 dependencies.
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first so Docker can cache this layer between code edits.
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the application code and your research data.
COPY src/ ./src/

# Streamlit's default port. Must match `app_port` in README.md's metadata header.
EXPOSE 8501

# Lets Spaces (and Docker) know the app is healthy.
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "src/streamlit_app.py", \
            "--server.port=8501", "--server.address=0.0.0.0"]
