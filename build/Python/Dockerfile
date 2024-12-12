FROM python:3.10.16-slim-bookworm

# Installa alcune utility necessarie per lo sviluppo (come git, curl, vim) come root
RUN apt-get update && apt-get install -y \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Creazione utente
ARG USERNAME=mott
RUN useradd -m -s /bin/bash $USERNAME
USER $USERNAME

# Imposta il direttorio di lavoro come la cartella dell'utente
RUN mkdir /home/$USERNAME/ESA_Interferometric_Mission
WORKDIR /home/$USERNAME/ESA_Interferometric_Mission

# Installa pip e le dipendenze Python
COPY --chown=$USERNAME:$USERNAME requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
# Imposta il comando di default
CMD ["tail", "-f", "/dev/null"]