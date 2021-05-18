## Setup

```
$ sudo apt-get -y update
$ sudo apt-get -y install virtualenv
$ virtualenv env  --python=python3
$ . env/bin/activate
$ pip install -r requirements.txt
```

## Run

```
$ . env/bin/activate
$ python server.py 
Listening on http://0.0.0.0:8888
```

## Test

```
$ curl localhost:8888/
Hello, world
```

```
$ curl 54.146.246.126:8888/info
Region: us-east-1
AZ: us-east-1a
```
