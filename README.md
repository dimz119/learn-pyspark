# learn-pyspark

PySpark 강의 예제 모음입니다. 노트북(`lecture*.ipynb`)과 스트리밍 스크립트(`spark_kafka_*.py`)로 구성되어 있습니다.

## 두 가지 실행 환경

| 파일 | Spark | Scala | 용도 |
| --- | --- | --- | --- |
| `docker-compose.yml` | 3.4.3 (노트북 3.5.0) | 2.12 | 기존 강의 자료 기준. 아래 예제 명령어가 이 환경 기준입니다. |
| `docker-compose.spark4.yml` | 4.2.0 | 2.13 | 최신 버전 실습용 |

두 파일은 포트가 겹치므로 **동시에 띄우지 마세요.**

```
# 기본 (Spark 3.x)
$ docker compose up -d

# Spark 4.2
$ docker compose -f docker-compose.spark4.yml up -d
```

### 이미지에 대한 참고

Bitnami가 2025-08 부터 무료 이미지 배포를 중단해서 `bitnami/spark`, `bitnami/kafka`,
`bitnami/cassandra` 태그가 모두 사라졌습니다. 그래서:

- `docker-compose.yml` 은 아카이브 저장소인 `bitnamilegacy/*` 를 사용합니다.
  기존 3.x 동작을 그대로 재현하지만 보안 업데이트는 더 이상 제공되지 않습니다.
- `docker-compose.spark4.yml` 은 유지보수되는 `apache/spark`, `apache/kafka`,
  Docker Official `cassandra` 로 교체했습니다.

노트북 이미지는 `jupyter/pyspark-notebook` 이 deprecated 되어 Spark 4 쪽은
`quay.io/jupyter/pyspark-notebook` 을 사용합니다.

## 노트북 접속

```
$ docker compose up -d
$ docker compose logs pyspark | grep 127.0.0.1:8888
     or http://127.0.0.1:8888/lab?token=aff690ec32bd72248eb8f3b9c3ecced37135bdc5a70d782a
```

출력된 토큰 URL을 브라우저에서 엽니다.

컨테이너 없이 노트북 이미지만 단독으로 쓰려면:

```
$ docker run -it --rm -p 8888:8888 -v "${PWD}":/home/jovyan/work \
    --user root -e NB_GID=100 -e GRANT_SUDO=yes \
    jupyter/pyspark-notebook:spark-3.5.0
```

## 실행 중인 컨테이너

```
$ docker compose ps
IMAGE                                  STATUS                   PORTS
docker.io/bitnamilegacy/spark:3.4      Up 5 minutes             0.0.0.0:4040->4040/tcp, 0.0.0.0:8080->8080/tcp, 0.0.0.0:18080->18080/tcp
docker.io/bitnamilegacy/spark:3.4      Up 5 minutes
jupyter/pyspark-notebook:spark-3.5.0   Up 5 minutes (healthy)   0.0.0.0:8888->8888/tcp
bitnamilegacy/kafka:3.4                Up 5 minutes             0.0.0.0:9092->9092/tcp, 0.0.0.0:9094->9094/tcp
bitnamilegacy/cassandra:4.0.11         Up 5 minutes             0.0.0.0:9042->9042/tcp
```

Web UI: Spark Master `8080`, History Server `18080`, Jupyter `8888`

## spark-submit 사용법

> **중요:** 아래 명령어들은 모두 **컨테이너 안에서** 실행해야 합니다.
> 스크립트가 `kafka:9092`, `cassandra`, `spark://spark:7077` 같은 컨테이너 호스트명을
> 사용하기 때문에, 맥/윈도우 호스트에서 그대로 실행하면
> `UnknownHostException: spark` 로 실패합니다.

```
# spark master 컨테이너로 진입
$ docker compose exec spark bash
$ cd /opt/bitnami/spark/work
```

기본 사용:

```
spark-submit --master spark://spark:7077 <python_file_location>
```

Kafka 연동:

```
spark-submit --master spark://spark:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 \
  spark_kafka.py
```

Kafka + Cassandra 연동:

```
spark-submit --master spark://spark:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,com.datastax.spark:spark-cassandra-connector_2.12:3.4.1 \
  spark_kafka_static_join.py
```

### Scala 버전 주의

`--packages` 좌표 끝의 `_2.12` 는 **Spark 런타임의 Scala 버전과 반드시 일치**해야 합니다.
어긋나면 의존성 다운로드는 성공해도 실행 중에 `NoClassDefFoundError: scala/Serializable` 로 죽습니다.

| 환경 | Scala | 좌표 예시 |
| --- | --- | --- |
| `docker-compose.yml` (Spark 3.4) | 2.12 | `org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1` |
| `docker-compose.spark4.yml` (Spark 4.2) | 2.13 | `org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0` |

Spark 4.2 에서 Kafka 를 읽는 경우:

```
spark-submit --master spark://spark:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0 \
  spark_kafka.py
```

참고로 `spark-cassandra-connector` 는 아직 3.5.1 이 최신이라 Spark 4.x 용 빌드가 없습니다.
Cassandra 예제는 `docker-compose.yml`(Spark 3.x) 환경에서 실행하세요.

### `--packages` 다운로드가 실패할 때

```
[NOT FOUND  ] commons-logging#commons-logging;1.1.3!commons-logging.jar
:: commons-logging#commons-logging;1.1.3
Exception in thread "main" java.lang.RuntimeException: [download failed: ...]
```

로컬 `~/.m2` 캐시에 `.pom` 만 있고 `.jar` 이 없을 때 발생합니다.
Ivy 가 "로컬에 있다"고 판단해 Maven Central 을 조회하지 않기 때문에,
해당 항목을 지우고 다시 받으면 해결됩니다.

```
$ rm -rf ~/.m2/repository/commons-logging/commons-logging/1.1.3
```

## Spark 워커 늘리기

```
docker compose up -d --scale spark-worker=2
```

## History Server

`docker-compose.yml` 은 18080 포트만 열어두고 데몬은 자동 실행되지 않습니다.
마스터 컨테이너에서 직접 띄웁니다.

```
$ docker compose exec spark bash
$ ./sbin/start-history-server.sh
```

`docker-compose.spark4.yml` 에는 `spark-history` 서비스가 분리되어 있어 별도 실행이 필요 없습니다.

## Kafka

```
$ docker compose exec kafka bash
$ cd /opt/bitnami/kafka/bin

# 토픽 생성
./kafka-topics.sh --create --topic <topic> --bootstrap-server localhost:9092

# 토픽 삭제
./kafka-topics.sh --bootstrap-server 127.0.0.1:9092 --delete --topic <topic>

# 콘솔 프로듀서
./kafka-console-producer.sh --bootstrap-server 127.0.0.1:9092 --topic <topic> \
  --producer.config /opt/bitnami/kafka/config/producer.properties

# 콘솔 컨슈머
./kafka-console-consumer.sh --bootstrap-server 127.0.0.1:9092 --topic <topic> \
  --consumer.config /opt/bitnami/kafka/config/consumer.properties
```

Spark 4 스택(`apache/kafka`)은 경로와 환경변수 규약이 다릅니다.
바이너리는 `/opt/kafka/bin` 에 있고, `--producer.config` 옵션 없이 사용합니다.

## Cassandra

```
$ docker compose exec cassandra cqlsh -u cassandra -p cassandra
```

`bitnamilegacy` 이미지는 기본 인증이 켜져 있어 `-u cassandra -p cassandra` 가 필요합니다.

`spark_kafka_static_join.py` 가 사용하는 스키마:

```sql
CREATE KEYSPACE test_db WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
use test_db;
CREATE TABLE users(login_id text PRIMARY KEY, user_name text, last_login timestamp);
INSERT INTO users (login_id, user_name, last_login) VALUES ('100', 'Kim', '2023-09-01 00:00:00');
INSERT INTO users (login_id, user_name, last_login) VALUES ('101', 'Lee', '2023-09-01 01:00:00');
INSERT INTO users (login_id, user_name, last_login) VALUES ('102', 'Park', '2023-09-01 02:00:00');
select * from users;
```

Spark 4 스택은 Docker Official `cassandra:5.0` 이라 인증이 꺼져 있고, 컨테이너 안에서는
`rpc_address` 가 `0.0.0.0` 이라 호스트를 명시해야 합니다.

```
$ docker compose -f docker-compose.spark4.yml exec cassandra cqlsh cassandra
```

## 테스트 데이터 생성

https://github.com/lucapette/fakedata

```
fakedata --limit 1000 --separator=, name email int:10000,200000 >> income.csv
```
