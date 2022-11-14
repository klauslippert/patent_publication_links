# adopt those 2 lines for your username
#sudo chown -R lippert:lippert data/postgresql/
#sudo chown -R lippert:lippert code/
#


export image=pat_pub_links:1.0
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
