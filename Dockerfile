###########################################
# Throwaway image with C compiler installed

FROM ubuntu:20.04

ENV PYTHONUNBUFFERED 1
#RUN python -m pip install pip==9.0.3
#RUN pip install cython
#RUN pip install --install-option="--prefix=/install" --trusted-host pypi.python.org -r /tmp/requirements.txt
RUN apt-get update
RUN apt-get install -y build-essential python3 python3-dev python3-pip locales

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN pip3 install --trusted-host pypi.python.org cython
RUN pip3 install --trusted-host pypi.python.org --upgrade pip setuptools wheel
#RUN pip3 install --trusted-host pypi.python.org pandas

COPY ./requirements.txt /tmp/
RUN pip3 install --trusted-host pypi.python.org -r /tmp/requirements.txt

###########################################
# Image WITHOUT C compiler but WITH uWSGI

#FROM base
#COPY --from=builder /install/ /usr/local
#COPY --from=builder /root/.local/ /usr/.local

# RUN apk add --no-cache libxml2 libxslt-dev jpeg-dev postgresql-dev

USER 1000
WORKDIR /app

CMD [ "./check_email.py" ]
