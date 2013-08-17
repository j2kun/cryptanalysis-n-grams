#!/bin/bash

i=1; 
for line in `cat codes.txt`; 
do 
   echo $line | python test-substitution.py > code${i}.txt; 
   i=$((i+1)); 
done

