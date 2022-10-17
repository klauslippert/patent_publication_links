# grep "The fair-use policy" -l aa*/*xml  | wc -l

## 
mkdir DEL
##
for folder in *
  do
    mkdir DEL/$folder
  done

########

for folder in *
  do
    for file in `grep "The fair-use policy" -l $folder/*xml`
      do
        mv $file DEL/$file
      done
  done

