#!/usr/bin/bash

cd frontend; yarn install && yarn build; cd ..; rm -rf nginx/dist; cp -r frontend/dist nginx/dist