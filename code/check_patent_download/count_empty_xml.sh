rm cnt_empty_xml

for folder in *
  do 
    grep "fair-use policy" $folder/*.xml | wc -l >> cnt_empty_xml
  done

echo found in total patent xml with empty content:
awk '{sum += $1 } END { print sum }' cnt_empty_xml 

