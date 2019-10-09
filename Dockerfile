FROM centos:7

RUN yum install -y python3 python3-pip

RUN pip3 install boto3

ENV LANG=en_US.UTF-8

