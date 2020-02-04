#!/usr/bin/env bash

set -o nounset
set -o pipefail
set -o errexit

# Add Docker’s official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

sudo apt-get update
sudo apt-get \
    install linux-image-extra-virtual \
    apparmor \
    -y --no-install-recommends

sudo apt-get remove \
    docker \
    docker-engine \
    docker.io \
    containerd \
    runc

VERSION_STRING=5:19.03.1~3-0~ubuntu-bionic
sudo apt-get install \
    docker-ce=${VERSION_STRING} \
    docker-ce-cli=${VERSION_STRING} \
    -y --no-install-recommends

sudo usermod -aG docker ubuntu
sudo usermod -aG docker app_user

sudo mkdir -p /etc/docker

# use iptables
cat << "EOF" | sudo tee /etc/docker/daemon.json

{
    "userland-proxy": false
}

EOF

# https://github.com/docker/docker-credential-helpers/issues/60#issuecomment-431784438
sudo rm -rf /usr/bin/docker-credential-secretservice

COMPOSE_VERSION=1.24.1
sudo curl \
    -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose

sudo curl \
    -L "https://raw.githubusercontent.com/docker/compose/${COMPOSE_VERSION}/contrib/completion/bash/docker-compose" \
    -o /etc/bash_completion.d/docker-compose

sudo systemctl enable docker
