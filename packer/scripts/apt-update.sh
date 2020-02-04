#!/usr/bin/env bash

##
#!/usr/bin/env bash

set -o nounset
set -o pipefail
set -o errexit

sudo apt-get update -qq
sudo apt-get upgrade -y -qq

# install some useful utilities
sudo apt-get install \
git \
build-essential \
unzip \
curl \
ntp \
ack-grep \
iotop \
htop \
jq \
apt-transport-https \
awscli \
-y -qq --no-install-recommends

# disable crash reporting for ubuntu
sudo apt-get purge apport -y

sudo useradd app_user -s /bin/bash
sudo usermod -aG app_user ubuntu
