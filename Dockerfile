FROM python:3.6.5-slim

RUN apt-get update && apt-get -y install gcc && \
    apt-get -y install g++ && apt-get -y install libxml2-dev libxslt1-dev zlib1g-dev procps libpcre3 libpcre3-dev vim less

RUN apt-get -y install git
# setup User Group
RUN useradd --shell /bin/bash --create-home worker
USER worker
SHELL ["/bin/bash", "-c"]
WORKDIR /home/worker
ENV PATH="/home/worker/.local/bin:${PATH}"

RUN pip install awscli --upgrade --user

# Setup Virtual Environment
RUN pip install --user --upgrade pip
RUN pip install --user virtualenv
RUN mkdir ~/.environments
RUN virtualenv ~/.environments/qcs
ENV VIRTUAL_ENV ~/.environments/qcs
ENV PATH /home/worker/.environments/qcs/bin:$PATH
RUN pip install nltk
RUN python -m nltk.downloader wordnet
RUN python -m nltk.downloader omw-1.4

RUN mkdir -p QCS/app/logs/
ADD requirements.txt .
RUN pip install -r requirements.txt
# Add project & it's dependencies
ADD --chown=worker:worker . QCS

WORKDIR /home/worker/QCS/app

ARG BUCKET_NAME

# RUN uwsgi --build-plugin https://github.com/Datadog/uwsgi-dogstatsd

EXPOSE 8080

CMD [ "uwsgi", "--ini", "qcs.ini" ]