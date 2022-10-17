#!/bin/bash
## POSTGRES
echo change permissions of postgresql data folder
chown -R postgres:postgres /home/user/data/postgresql/main
##
echo change configureation in postgresql for new data folder
sed -i 's|/var/lib/postgresql/10/main|/home/user/data/postgresql/main|g' /etc/postgresql/10/main/postgresql.conf
##
echo change config for password
sed -i 's|peer|trust|g' /etc/postgresql/10/main/pg_hba.conf
service postgresql start
##
psql -U postgres -c "alter user postgres password 'postgres';"
sed -i 's|trust|md5|g' /etc/postgresql/10/main/pg_hba.conf
##
echo start postgresql
service postgresql restart
##
source "$HOME/.cargo/env"    #enable RUST
pip3 install -r /home/user/code/requirements.txt
python3 -c "import nltk; nltk.download('punkt')"

