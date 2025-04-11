# syntax=docker/dockerfile:1

# ---- Base Image ----
FROM python:3.10.17

# ---- Environment Setup ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---- Set Work Directory ----
WORKDIR /app

# ---- Install System Dependencies ----
RUN apt-get update && \
    apt-get install -y \
    curl \
    build-essential \
    portaudio19-dev \
    libportaudio2 \
    libsndfile1-dev \
    libasound2-dev \
    libsndfile1 \
    libatlas-base-dev \
    libfftw3-dev \
    libsndfile1-dev \
    libjack-dev \
    libreadline-dev \
    libssl-dev && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# ---- Copy the Policy Docs Folder ----
COPY policy_docs /app/policy_docs

# ---- Copy the README.md File ----
COPY README.md /app/
# ---- Install Poetry ----
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# ---- Copy Files ----
COPY pyproject.toml poetry.lock ./

# ---- Install Dependencies ----
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# ---- Copy Application Code ----
COPY . .

# ---- Debugging Step (Optional) ----
RUN ls -R /app/policy_docs

# ---- Run Server ----
CMD ["poetry", "run", "python", "main.py"]
