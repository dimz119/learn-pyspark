
# Start PySpark notebook docker
최근 https://hub.docker.com/r/jupyter/pyspark-notebook 다커 레지스트리에 따르면, image registry를 `quay.io`로 옮긴다는
내용이 나와있습니다. 일단 아직까지는 Dockerhub으로 이미지를 다운 받은 거에 아무런 문제가 없으니 크게 신경쓰시지는 않으셔도 됩니다.

다만 혹시나 해서 제가 사용할 수 있는 정확한 버전으로 명령어를 바꾸겠습니다.

```
# use docker command
# download notebook image(with spark-3.5.0)
$ docker pull jupyter/pyspark-notebook:spark-3.5.0

# start the docker with spark-3.5.0
$ docker run -it --rm -p 8888:8888 -v "${PWD}":/home/jovyan/work --user root -e NB_GID=100 -e GRANT_SUDO=yes -e GRANT_SUDO=yes jupyter/pyspark-notebook:spark-3.5.0

or

# use docker compose
$ docker compose up

# list the running docker containers
$ docker ps
CONTAINER ID   IMAGE                      COMMAND                  CREATED         STATUS                   PORTS                                                                      NAMES
dadc6458f9fe   bitnami/spark:3.4          "/opt/bitnami/script…"   6 minutes ago   Up 6 minutes             0.0.0.0:4040->4040/tcp, 0.0.0.0:8080->8080/tcp, 0.0.0.0:18080->18080/tcp   pyspark-spark-1
0042c7d1e77d   jupyter/pyspark-notebook   "tini -g -- start-no…"   6 minutes ago   Up 6 minutes (healthy)   4040/tcp, 0.0.0.0:8888->8888/tcp                                           pyspark-pyspark-1
9a47134a919e   bitnami/spark:3.4          "/opt/bitnami/script…"   6 minutes ago   Up 6 minutes                                                                                        pyspark-spark-worker-1
4d441801b11a   bitnami/kafka:3.4          "/opt/bitnami/script…"   6 minutes ago   Up 6 minutes             0.0.0.0:9092->9092/tcp, 0.0.0.0:9094->9094/tcp                             pyspark-kafka-1

# find the pyspark container id(where 0042c7d1e77d should be replaced by yours)
$ docker logs 0042c7d1e77d
...
[C 2023-09-04 23:25:30.364 ServerApp]
    To access the server, open this file in a browser:
        file:///home/jovyan/.local/share/jupyter/runtime/jpserver-19-open.html
    Or copy and paste one of these URLs:
        http://0042c7d1e77d:8888/lab?token=038e039501517f1005cc9d05311efc4134be87a95a680ac1
     or http://127.0.0.1:8888/lab?token=038e039501517f1005cc9d05311efc4134be87a95a680ac1

# click the last link to open the notebook
```

# Generate fake data
https://github.com/lucapette/fakedata
fakedata --limit 1000 --separator=, name email int:10000,200000 >> income.csv

# Start history server after ssh into the spark master container
./sbin/start-history-server.sh

# How to use spark-submit
spark-submit --master spark://spark:7077 <python_file_location>

# Start Spark with multiple worker
docker compose up --scale spark-worker=2

# Start Spark with Kafka
spark-submit --master spark://spark:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 spark_kafka.py

# Write Kafka event
```
cd /opt/bitnami/kafka/bin

# create a topic
./kafka-topics.sh --create --topic <topic> --bootstrap-server localhost:9092

# delete the topic
./kafka-topics.sh --bootstrap-server 127.0.0.1:9092  --delete --topic <topic>

# start console producer
./kafka-console-producer.sh --bootstrap-server 127.0.0.1:9092 --topic <topic> --producer.config /opt/bitnami/kafka/config/producer.properties

# start console consumer
./kafka-console-consumer.sh --bootstrap-server 127.0.0.1:9092 --topic <topic> --consumer.config /opt/bitnami/kafka/config/consumer.properties
```

# Start Spark with Kafka & Cassandra
spark-submit --master spark://spark:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,com.datastax.spark:spark-cassandra-connector_2.12:3.4.1 spark_kafka_static_join.py

# Cassandra
```
cqlsh -u cassandra -p cassandra
CREATE KEYSPACE test_db WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
use test_db;
CREATE TABLE users(login_id text PRIMARY KEY, user_name text, last_login timestamp);
INSERT INTO users (login_id, user_name, last_login) VALUES ('100', 'Kim', '2023-09-01 00:00:00');
INSERT INTO users (login_id, user_name, last_login) VALUES ('101', 'Lee', '2023-09-01 01:00:00');
INSERT INTO users (login_id, user_name, last_login) VALUES ('102', 'Park', '2023-09-01 02:00:00');
select * from users;
```
