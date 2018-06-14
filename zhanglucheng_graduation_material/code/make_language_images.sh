#!/bin/bash

mkdir /home/kongkong/language_images && cd /home/kongkong/language_images
cat > Dockerfile << EOF
# Version:0.0.1
FROM kongkongkkk/base_images:latest
MAINTAINER kongkongkkk "707249853@qq.com"
RUN yum install openssh-clients -y \
    && yum install net-tools -y \
    && yum install wget -y \
    && wget https://bootstrap.pypa.io/get-pip.py --no-check-certificate \
    && python get-pip.py \
    && pip install --upgrade pip \
    && pip install scipy \
    && pip install numpy \
    && pip install scikit-learn
EOF

docker build -t"kongkongkkk/language_images" .
docker pull kongkongkkk/language_images