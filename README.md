# PLATICA_Backend
Backend of PLATICA mobile application running on Flask

Frontend: https://github.com/evanj354/ChatUI

## Installation

Make sure you have Python 3 and virtualenv installed:

```sh
$ python --version
$ virtualenv --version
```
Create a virtualenv to manage dependencies:

```sh
$ virtualenv env
```

Activate your environment and install dependencies:

```sh
(env) $ pip install -r requirements.txt
```
## Configure Database

```sh
(env) $ flask db migrate -m "migrate message"
(env) $ flask db upgrade
```

## Running the backend

```sh
(env) $ flask run -h <IP>
```
