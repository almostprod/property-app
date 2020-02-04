#!/usr/bin/env bash

# It's often helpful to just go ahead and do this.

set -o nounset
set -o pipefail
set -o errexit

# specify the new file limits explicitly
cat << "EOF" | sudo tee -a /etc/security/limits.conf

# bump up all user file limits to 10k
*                soft    nofile          10000
*                hard    nofile          10000

EOF

# update common PAM sessions to pick up the new limit
cat << "EOF" | sudo tee -a /etc/pam.d/common-session

# add for file limit increase
session required pam_limits.so

EOF
