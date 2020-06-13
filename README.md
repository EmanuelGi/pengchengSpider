### YLS

---

#### Require

- MySQL/MariaDB
- Node.js
- Python2.7
- mysql-python module
- scrapy module
- scrapy-redis module
- requets module

#### Build

The required tools is almost ready in project.

- install redis: `cd redis-4.0.1` and just run `make`
- install NiuTransServer(For the sake of insurance, you'd better run the command below in a new account):

``` shell
cd NiuTransServer/service/
sh ./install.sh
source ~/.bashrc
```

- install node requires:

```shell
cd Front
npm install # I recommend you using cnpm, it would be faster
```

#### Setup

To setup ES, just run:

```shell
bash ./es_index.sh delete
bash ./es_index.sh create
```

You should create a MySQL database `YLS`, and then load the MySql Tables:

```shell
mysql -u<YOUR-USER-NAME> -p<YOUR-PASSWORD> YLS < db.sql
```

And before start the whole project, in `config.py`, you can customize the `Redis`, `MySQL`, `NiuTransServer` and `ES` with their hosts and ports, etc. 

#### Run

- start elasticsearch: run `bash ./start_es.sh`
- start redis: run `bash ./start_redis.sh`
- start spider: run `bash ./start_spider.sh`
- start NiuTransServer: run `bash ./start_trans.sh`
- start front search page: run `bash ./start_search.sh`
- start ES daemon to automatic add data: run `bash ./es_daemon.sh`
- enable Timer to clear outdated fingerprint every day at 00:00: use `crontab`  and run `/timer.sh` script at the frequency you want
- enable incrementally crawl the web page: also use `crontab` and run the `run_client.sh` at the time you want,
noticed that you can add the new `start_urls` in `recursive_crawler/health_websites_ch.xlsx`.

#### Reference

- [NiuTransServer](http://www.niutrans.com/build-niutrans/ch/niutrans_linux.html)
- [Scrapy-Redis](https://github.com/rmax/scrapy-redis)
- [redis-py](https://github.com/andymccurdy/redis-py)
- [Redis](http://www.redis.cn/)
- [elasticsearch](https://elasticsearch.cn/)
- [analysis-ik](https://github.com/medcl/elasticsearch-analysis-ik)
- [requests](http://docs.python-requests.org/zh_CN/latest/user/quickstart.html)

#### Good Luck!
