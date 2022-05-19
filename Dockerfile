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
RUN virtualenv ~/.environments/dynamite
ENV VIRTUAL_ENV ~/.environments/dynamite
ENV PATH /home/worker/.environments/dynamite/bin:$PATH
RUN pip install nltk
RUN python -m nltk.downloader wordnet
RUN python -m nltk.downloader omw-1.4

RUN mkdir -p dynamite/app/logs/
ADD requirements.txt .
RUN pip install -r requirements.txt
# Add project & it's dependencies
ADD --chown=worker:worker . dynamite

WORKDIR /home/worker/dynamite/app


# RUN uwsgi --build-plugin https://github.com/Datadog/uwsgi-dogstatsd

EXPOSE 8080

CMD [ "uwsgi", "--ini", "dynamite.ini" ]