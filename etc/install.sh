#!/bin/bash

NAME=pybindfs
DST_DIR=${HOME}/.local/share
mkdir -p ${DST_DIR}/icons
mkdir -p ${DST_DIR}/applications

cp -f ${NAME}.png  ${DST_DIR}/icons
cp -f ${NAME}.desktop ${DST_DIR}/applications
cp -fR ${NAME} ${DST_DIR}


