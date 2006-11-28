#!/bin/bash
for i in `ls *.xsd`
do
  basename=${i%%.xsd}
  if [ ! -d ./doc/${basename} ] 
  then 
    mkdir -p ./doc/${basename}
  fi
  xsddoc -t "${basename}" -o ./doc/${basename} -verbose $i
done

