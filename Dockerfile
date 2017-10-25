FROM ubuntu:16.04

RUN apt-get update && apt-get upgrade --assume-yes

RUN apt-get install --assume-yes        \
        openssh-server                  \
        python3-dev                     \
        python3-pip

RUN pip3 install virtualenv

RUN mkdir -p /var/run/sshd
RUN echo 'root:password' | chpasswd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/session\s*required\s*pam_loginuid.so/session optional pam_loginuid.so/g' /etc/pam.d/sshd

RUN mkdir -p /root/animarender-test
RUN python3 -m virtualenv /root/animarender-test/.venv
