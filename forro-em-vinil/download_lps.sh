 #!/bin/bash
let count=0
while read p; do
  ((count++))
  echo "Downloading file #${count}: ${p}" 
  megadl $p
done <'tudo do forro em vinil.txt'