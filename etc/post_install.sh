# ! /bin/bash

apt-get -y update
apt-get install -y git python python-pip
git clone https://github.com/dlux/dluxparser.git
chwon -r ubuntu:ubuntu dluxparser
pushd dluxparser
pip install -e ./
