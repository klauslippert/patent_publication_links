
FROM ubuntu:18.04

RUN apt-get update && apt-get install -y apt-utils 
RUN apt-get update && apt-get install -y locales locales-all
ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
#RUN locale-gen en_US.UTF-8

RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y tzdata

RUN apt-get update &&\
    apt-get install -y python3 &&\
    apt-get install -y parallel &&\
    apt-get install -y wget nano &&\
    apt-get install -y python3-pip &&\
    python3 -m pip install -U --force-reinstall pip &&\
    apt-get install -y libpq-dev python-dev tilde &&\
    apt-get install -y postgresql-plpython3
#RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y tzdata 

RUN wget https://sh.rustup.rs -O install_rust.sh &&\
    chmod u+x install_rust.sh &&\
    sh install_rust.sh -y
    

#ENV LC_ALL=en_US.UTF-8
#ENV LANG=en_US.UTF-8
########ENV DEBIAN-FRONTEND="noninteractive" 
#########ENV TZ="Europe/London"


#EXPORT DEBIAN-FRONTEND=noninteractive 
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y postgresql postgresql-contrib 
#RUN apt-get install -y wget nano curl
#RUN apt-get install -y python3-pip 
#RUN python3 -m pip install -U --force-reinstall pip
#RUN apt-get install -y libpq-dev python-dev tilde
# ######## POSTGRES
# Adjust PostgreSQL configuration so that remote connections to the
# database are possible.
RUN echo "host all  all    0.0.0.0/0  trust" >> /etc/postgresql/10/main/pg_hba.conf
RUN echo "listen_addresses='*'" >> /etc/postgresql/10/main/postgresql.conf
# Expose the PostgreSQL port
EXPOSE 5432
# start
#RUN service postgresql start

# change database location
#     is done later in entrypoint.sh..  perhaps move it to here
# set passwd for usr postgres
#RUN psql -U postgres -c "alter user postgres password 'postgres'";




RUN useradd -ms /bin/bash user -p "$(openssl passwd -1 user123)"

#USER user
WORKDIR /home/user

#RUN useradd postgres

COPY entrypoint.sh /home/user
RUN ["chmod", "a+x", "/home/user/entrypoint.sh"]




# make python3 easily accessable
#RUN alias python=python3



#USER user   

RUN mkdir /home/user/data

# for development this folder is mounted and not copied.
# TODO change this later to COPY (**what??)
#COPY code /home/user/code


#RUN mkdir /home/user/data
#RUN mkdir /home/user/data/postgresql


#RUN mkdir /home/user/data/supplement
#COPY data/supplement /home/user/data/supplement


#RUN pip3 install -r /home/user/code/requirements.txt


#COPY code /home/user/code

## install RUST (needed for BERT.. pytorch in detail)
#RUN curl https://sh.rustup.rs -sSf | sh
############################################
# number (integer as string) of cores downloading EPO-xml simultaniously
ENV njobs_epo_download='10'    
# EPO might block you, if too much in parallel
# needed in:
ENV njobs_epo_upload=20        
# maximum half cores      # not implemented yet 
# needed in:    funct02_04_patent_xml_upload.sh
ENV njobs_country_extraction_affiliation=25  
# not implemented yet
    # needed in:    funct04_02_country_extract.py
ENV njobs_patent_name_processing=20
# not implemented yet
ENV njobs_mesh_extraction=30
# not implemented yet



#COPY test.txt /home/user

#RUN pip3 install -r /home/user/code/requirements.txt


ENTRYPOINT /home/user/entrypoint.sh && /bin/bash
#ENTRYPOINT service postgresql start && /bin/bash
#ENTRYPOINT /bin/bash
