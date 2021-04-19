#!/usr/bin/env bash

ODIR=$1
EXP=$2
YR=$3

echo "Running my script in ${PWD} on directory ${ODIR}..."
echo "Output files: $(ls "${ODIR}"/ICMGG"${EXP}"+"${YR}"??)"
echo "The requested variables are ""$4"""
