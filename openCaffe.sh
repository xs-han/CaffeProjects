#!/bin/bash
if [ $# = 0  ]; then
    echo use default bvlc/caffe:gpu as the image
    IMAGE=bvlc/caffe:gpu
elif [ $# = 1 ]; then
    echo image file: $1
    IMAGE=$1
else
    echo usage: $0 dockerImageName
    exit 1
fi

CHECKIMAGE=${IMAGE/:/ *}
CHECKRES=`docker images | grep "^${CHECKIMAGE}  *"`
if [ "$CHECKRES" = "" ]; then
    echo the input image does not exist
    exit -1
else
    echo image $IMAGE found!
fi
# Firstly we need to add current user in user group: docker & nvidia-docker

#add right for docker to display
xhost +local:docker
xhost +local:nvidia-docker

# add display port
# add mounted display files: /tmp/.X11-unix-->/tmp/.X11-unix
# add mounted workspace directory: ~/dl/workspace-->/workspace
# add mounted PycharmProjects directory: ~/dl/PycharmProjects-->/root/PycharmProjects
nvidia-docker run -i -t -e DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ${PWD}/workspace:/workspace \
    -v ${PWD}/PycharmProjects:/root/PycharmProjects \
    ${IMAGE}
