FROM python:3.10-bookworm

WORKDIR /arpae-astep

RUN wget https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm packages-microsoft-prod.deb


RUN apt-get update && apt-get install -y \
    locales \
    build-essential \
    curl \
    dotnet-runtime-6.0 \
    software-properties-common \
    qt6-base-dev \
    git \

    && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

ENV LANG en_US.utf8

COPY . /arpae-astep

RUN pip3 install -r requirements.txt

EXPOSE 8501/tcp
EXPOSE 8501/udp

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "/arpae-astep/Code/Streamlit-code/Welcome.py", "--server.port=8501", "--server.address=0.0.0.0"]
