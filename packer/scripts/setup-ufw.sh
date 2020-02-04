#!/usr/bin/env bash

set -o nounset
set -o pipefail
set -o errexit

sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
