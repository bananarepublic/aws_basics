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
$ export EC2_HOST=54.146.246.126
```

```
$ curl $EC2_HOST:8888/
Hello, world
```

```
$ curl $EC2_HOST:8888/info
Region: us-east-1
AZ: us-east-1a
```

### Create local file

```
$ echo 'Hello, world!' > file.txt
```

### Create files

```
$ curl -i $EC2_HOST:8888/files -F files=@file.txt
```

### List all files

```
$ curl -i $EC2_HOST:8888/files/
```

### Get file

```
$ curl -i $EC2_HOST:8888/files/file.txt
```

### Delete file

```
$ curl -XDELETE $EC2_HOST:8888/files/file.txt
```
