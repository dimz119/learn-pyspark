
# Start docker
docker run -it --rm -p 8888:8888 -v /Users/seungjoonlee/git/pyspark:/home/jovyan/work --user root -e NB_GID=100 -e GRANT_SUDO=yes -e GRANT_SUDO=yes jupyter/pyspark-notebook

# Generate fake data
https://github.com/lucapette/fakedata
fakedata --limit 1000 --separator=, name email int:10000,200000 >> income.csv
