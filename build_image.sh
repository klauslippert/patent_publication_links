sudo chown -R lippert:lippert data/postgresql/
sudo chown -R lippert:lippert code/

export image=pat_pub_links:0.1
export mypath=`pwd`
echo $mypath


docker build -t $image .

echo "##########################################"
echo access the postgres from outside container:
echo psql -h localhost -p 6543 -U postgres
echo "##########################################"


## for development purpose hang in the code folder
docker run -it \
-v $mypath/data/patent:/home/user/data/patent \
-v $mypath/data/publication:/home/user/data/publication \
-v $mypath/data/postgresql:/home/user/data/postgresql \
-v $mypath/data/supplement:/home/user/data/supplement \
-v $mypath/data/figures:/home/user/data/figures \
-v $mypath/code:/home/user/code \
-p 6543:5432 \
$image /bin/bash

#-v $mypath/data/postgresql:/home/user/data/postgresql \
#-v $mypath/data/postgresql/main:/var/lib/postgresql/10/main \
## --user "$(id -u):$(id -g)" \
##/var/lib/postgresql/10/main/base \
##
##-v $mypath/data/postgresql/base:/var/lib/postgresql/10/main/base \
##-v $mypath/data/postgresql:/home/user/data/postgresql \
