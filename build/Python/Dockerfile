FROM python:3.11-slim

ARG USERNAME=mott
RUN useradd -m -s /bin/bash $USERNAME
USER $USERNAME
    
RUN mkdir /home/$USERNAME/ESA_Interferometric_Mission
WORKDIR /home/$USERNAME/ESA_Interferometric_Mission

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
CMD ["tail", "-f", "/dev/null"]