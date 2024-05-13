FROM --platform=linux/amd64  python:3.9-slim

RUN rm -rf /etc/apt/trusted.gpg.d/*

RUN  apt-get update \
  && apt-get install -yqq curl \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf /etc/apt/trusted.gpg.d/* \
  && apt --fix-broken install 

RUN apt-get update

RUN apt-get -y install gnupg xvfb

COPY . .

COPY requirements.txt .

RUN chmod +x ./main.sh

RUN pip install -r ./requirements.txt

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update --fix-missing
RUN apt-get install -y google-chrome-stable

# install chromedriver
#RUN apt-get install -yqq unzip
#RUN wget -O /tmp/chromedriver-linux64.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chromedriver-linux64.zip
#RUN unzip /tmp/chromedriver-linux64.zip -d ./scrapper

ENV DISPLAY=:99

#CMD ["python","./main.py"]
ENTRYPOINT ["./main.sh"]
