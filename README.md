专科大数据技术数据可视化技术期末作业
### 数据库安装

```shell
$ rpm -ivh mysql84-community-release-el7-1.noarch.rpm
$ yum install mysql-community-server -y
$ systemctl enable --now mysqld.service
$ grep password /var/log/mysqld.log
2024-12-21T07:12:23.455945Z 6 [Note] [MY-010454] [Server] A temporary password is generated for root@localhost: !sTi00ziorWF
$ mysql -u root -p"!sTi00ziorWF"
mysql> ALTER USER USER() IDENTIFIED BY 'Pp340400.';
mysql> update mysql.user set host='%' where user ='root';
```

### openssl安装

```shell
$ yum install -y git gcc make openssl-devel bzip2-devel libffi-devel zlib-devel readline-devel sqlite-devel mysql-devel
$ tar -zxvf openssl-1.1.1t.tar.gz
$ cd openssl-1.1.1t/
$ ./config --prefix=/usr/local/openssl
$ make && make install
$ ln -s /usr/local/openssl/lib/libssl.so.1.1 /usr/lib/libssl.so.1.1
$ ln -s /usr/local/openssl/lib/libcrypto.so.1.1 /usr/lib/libcrypto.so.1.1
$ ldconfig
$ /usr/local/openssl/bin/openssl version
OpenSSL 1.1.1t  7 Feb 2023
```

### Python安装

```shell
$ tar -zxvf Python-3.9.2.tgz
$ cd Python-3.9.2
$ ./configure --prefix=/usr/local/python3.9 --with-openssl=/usr/local/openssl
$ make && make install
$ vi /etc/profile
export PATH=$PATH:/usr/local/python3.9/bin
$ python3.9 --version
Python 3.9.2
$ python3.9
Python 3.9.2 (default, Dec 21 2024, 02:30:51) 
[GCC 4.8.5 20150623 (Red Hat 4.8.5-44)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import ssl
>>> print(ssl.OPENSSL_VERSION)
OpenSSL 1.1.1t  7 Feb 2023
```

### 设置pip镜像源

```shell
pip3.9 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip3.9 config list
```

### nginx安装配置

```shell
server {
    listen 80;
    server_name 111.230.26.92;
    
    location / {
        proxy_pass http://127.0.0.1:8000; 
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    } 

    location /static/css/ {
        alias /root/Money/Money/Crawler/static/css/;
        autoindex on;
        access_log /var/log/nginx/static_access.log;
        error_log /var/log/nginx/static_error.log;
    }

    location /static/js/ {
        alias /root/Money/Money/Crawler/static/js/;
        autoindex on;
        access_log /var/log/nginx/static_access.log;
        error_log /var/log/nginx/static_error.log;
    }

    error_page 404 /404.html;
    location = /404.html {
        root /usr/share/nginx/html; 
        internal;
    }
}
```

```shell
chmod o+x /root/Money/Money/Crawler

chcon -R -t httpd_sys_content_t /root/Money/Money/Crawler/static/
```

##### 创建数据库表

```sql
CREATE DATABASE Money;

create table Britain_stocks
(
    id             bigint auto_increment
        primary key,
    name           varchar(100) not null,
    latest_price   float        null,
    previous_close float        null
);

create table hong_kong_stocks
(
    id             bigint auto_increment
        primary key,
    code           bigint      not null,
    name           varchar(25) not null,
    latest_price   float       null,
    previous_close float       null
);

create table US_shares_stocks
(
    id             bigint auto_increment
        primary key,
    name           varchar(50) not null,
    latest_price   float       null,
    previous_close float       null
);
```

##### 配置`settins.py`

```shell
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '<DBNAME>',
        'USER': '<USERNAME>',
        'PASSWORD': '<PASSWORD>',
        'HOST': '<IP>',
        'PORT': 3306,
    }
}

CELERY_BROKER_URL = 'redis://:<PASSWORD>@<IP>:6379/0'
CELERY_RESULT_BACKEND = 'redis://:<PASSWORD>@<IP>:6379/0'
```

##### 下载包

```shell
$ pip3.9 install -r .\requirements.txt
```

##### 启动项目

```shell
$ celery -A Crawler.celery beat -l info
$ celery -A Crawler.celery worker -l info --pool=solo
$ python3.9 manage.py migrate
$ python3.9 manage.py runserver 0.0.0.0:80
```

##### 其他命令

```shell
$ redis-cli -h <IP> -p 6379 -a <PASSWORD> FLUSHDB
$ redis-cli -h <IP> -p 6379 -a <PASSWORD> KEYS "*"
$ redis-cli -h <IP> -p 6379 -a <PASSWORD> SCAN 0 MATCH "*"
```

