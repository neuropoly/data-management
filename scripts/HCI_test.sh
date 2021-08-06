#!/bin/bash

printf "\nTesting 1MB file to /duke/histology"
printf "\n###################################\n"
dd if=/dev/zero of=~/duke/histology/test_HCI/tempfile bs=1M count=1 conv=fdatasync,notrunc status=progress
rm -f ~/duke/histology/test_HCI/tempfile

printf "\nTesting 1MB file to /duke/temp"
printf "\n###################################\n"
dd if=/dev/zero of=~/duke/temp/test_HCI/tempfile bs=1M count=1 conv=fdatasync,notrunc status=progress
rm -f ~/duke/temp/test_HCI/tempfile

printf "\nTesting 10MB file to /duke/histology"
printf "\n####################################\n"
dd if=/dev/zero of=~/duke/histology/test_HCI/tempfile bs=1M count=10 conv=fdatasync,notrunc status=progress
rm -f ~/duke/histology/test_HCI/tempfile

printf "\nTesting 10MB file to /duke/temp"
printf "\n###################################\n"
dd if=/dev/zero of=~/duke/temp/test_HCI/tempfile bs=1M count=10 conv=fdatasync,notrunc status=progress
rm -f ~/duke/temp/test_HCI/tempfile

printf "\nTesting 100MB file to /duke/histology"
printf "\n#####################################\n"
dd if=/dev/zero of=~/duke/histology/test_HCI/tempfile bs=1M count=100 conv=fdatasync,notrunc status=progress
rm -f ~/duke/histology/test_HCI/tempfile

printf "\nTesting 100MB file to /duke/temp"
printf "\n################################\n"
dd if=/dev/zero of=~/duke/temp/test_HCI/tempfile bs=1M count=100 conv=fdatasync,notrunc status=progress
rm -f ~/duke/temp/test_HCI/tempfile

printf "\nTesting 1GB file to /duke/histology"
printf "\n###################################\n"
dd if=/dev/zero of=~/duke/histology/test_HCI/tempfile bs=1M count=1024 conv=fdatasync,notrunc status=progress
rm -f ~/duke/histology/test_HCI/tempfile

printf "\nTesting 1GB file to /duke/temp"
printf "\n################################\n"
dd if=/dev/zero of=~/duke/temp/test_HCI/tempfile bs=1M count=1024 conv=fdatasync,notrunc status=progress
rm -f ~/duke/temp/test_HCI/tempfile

printf "\nTesting 10GB file to /duke/histology"
printf "\n####################################\n"
dd if=/dev/zero of=~/duke/histology/test_HCI/tempfile bs=1M count=10240 conv=fdatasync,notrunc status=progress
rm -f ~/duke/histology/test_HCI/tempfile

printf "\nTesting 10GB file to /duke/temp"
printf "\n####################################\n"
dd if=/dev/zero of=~/duke/temp/test_HCI/tempfile bs=1M count=10240 conv=fdatasync,notrunc status=progress
rm -f ~/duke/temp/test_HCI/tempfile