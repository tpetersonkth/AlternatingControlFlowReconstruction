#!/bin/bash

apt -y install default-jdk
apt -y install python3
apt -y install python3-pip
apt -y install nasm
apt -y install z3
pip3 install manticore[native]
