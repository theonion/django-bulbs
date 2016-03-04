#!/usr/bin/env bash
set -e

docker-compose -f docker-compose.ci.yml build

docker-compose -f ./docker-compose.ci.yml run py2_7_es1_4_4
docker-compose -f ./docker-compose.ci.yml run py2_7_es1_4_5
docker-compose -f ./docker-compose.ci.yml run py2_7_es1_7_5

docker-compose -f ./docker-compose.ci.yml run py3_4_es1_4_4
docker-compose -f ./docker-compose.ci.yml run py3_4_es1_4_5
docker-compose -f ./docker-compose.ci.yml run py3_4_es1_7_5

docker-compose -f ./docker-compose.ci.yml run py3_5_es1_4_4
docker-compose -f ./docker-compose.ci.yml run py3_5_es1_4_5
docker-compose -f ./docker-compose.ci.yml run py3_5_es1_7_5
