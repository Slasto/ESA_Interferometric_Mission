FROM python:3.11-slim

RUN useradd -m -s /bin/bash mott
USER mott
    
RUN mkdir /home/mott/ESA_Interferometric_Mission
WORKDIR /home/mott/ESA_Interferometric_Mission


COPY requirements.txt .
ENV PATH="/home/mott/.local/bin:${PATH}"
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
CMD ["tail", "-f", "/dev/null"]