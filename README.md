# theatre-api

Django REST Framework API for the ticketing service system of the theater.

## Installation and Setup

Python 3 and Docker must be already installed

### Clone git repository

```shell
git clone https://github.com/msymonovych/newspaper-agency
cd newspaper_agency
```

### Build and start Docker containers

```shell
docker-compose up --build
```

You can now access API by `http://127.0.0.1:8000/` address

## Features

* JWT Token Authentication 
* Admins can create Plays and manage them directly by website interface
* Users can make reservations for performances
* Admin panel /admin/
* Have understandable documentation at /api/doc/swagger/
* Creating theatre halls
* Filtering plays and performances

## DB Structure
![image_2024-04-08_23-04-07](https://github.com/msymonovych/theatre-api-service/assets/87976005/951faedd-7bc0-4ecf-b70a-4bf5b1face1a)
