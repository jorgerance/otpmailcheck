#!/bin/bash

git pull
docker service rm otpmail_runner
docker image build -t otpmail .
docker stack deploy -c docker-compose.yml otpmail
docker service logs -f otpmail_runner
