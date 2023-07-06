# need a nvidia base image so it can acces GPUs
FROM nvidia/cuda:12.0.1-base-ubuntu22.04
CMD nvidia-smi

# optional, set author
MAINTAINER abigail.robinson@natgeo.su.se

# set working dir. If it doesn't exist then it will make one
WORKDIR /home/deepwetlands

# install dependancies
RUN apt update && apt install -y --no-install-recommends python3-dev python3-pip python3-setuptools binutils libproj-dev gdal-bin
#gdal-bin python-gdal python3-gdal

# Set python3 as the default version
#RUN ln -s /usr/bin/pip3 /usr/bin/pip
#RUN ln -s /usr/bin/python3 /usr/bin/python

RUN echo $PATH

# upgrade pip
RUN pip3 -q install pip --upgrade

# copy requirements.txt to work dir and install the python packages
COPY requirements.txt /home/deepwetlands

# copy env file
COPY .env /home/deepwetlands

# add wetlands requirements
RUN pip3 install -r /home/deepwetlands/requirements.txt

# copy code to working directory
ADD wetlands .
RUN mkdir -p /home/deepwetlands/wetlands
COPY wetlands /home/deepwetlands/wetlands

# not sure what to do about data; maybe add that manually outside of docke



