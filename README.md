# Loki
Loki is a HTTP mocking server that allows user to define API definitions using json files.

### Local development

1. Clone project from github `git clone https://github.com/the-sloth-dev/loki`
2. Install and configure [python](https://www.python.org/downloads/)
3. Install and configure [pip](https://pypi.org/project/pip/)
4. Install project requirements `pip install -r requirements.txt`
5. Define your API mock definitions. See **Mocking Endpoints**
6. Start application by running `src/app.py`

### Mocking Endpoints

Endpoints can be mocked by providing an API definitions using json files.
The location of the JSON file can be declared via the environment variable `MOCK_ENDPOINTS_JSON`.

Example declaring the environment variable:
```
export MOCK_ENDPOINTS_JSON=/tmp/mock_endpoints.json
```

Sample of `mock_endpoints.json`:
```
[
    {
        "method": "GET",
        "path": "/api/v1/users",
        "status_code": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "response_body": {
            "users": [
                {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john.doe@example.com"
                },
                {
                    "id": 2,
                    "name": "Jane Doe",
                    "email": "jane.doe@example.com"
                }
            ]
        }
    },
    {
        "method": "POST",
        "path": "/api/v1/login",
        "status_code": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "response_body": {
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        }
    }
]
```

Use curl to verify that your endpoints have been mocked:
```
$ curl -i -w "\n" -H "Content-Type: application/json" -H "Accept: application/json" -X POST http://localhost:5000/api/v1/login
HTTP/1.1 200 OK
Server: Werkzeug/2.1.2 Python/3.9.2
Date: Sun, 26 Feb 2023 17:31:00 GMT
Content-Type: application/json
Content-Length: 49
Connection: close

{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}

$ curl -i -w "\n" -H "Content-Type: application/json" -H "Accept: application/json" -X GET http://localhost:5000/api/v1/users
HTTP/1.1 200 OK
Server: Werkzeug/2.1.2 Python/3.9.2
Date: Sun, 26 Feb 2023 17:31:51 GMT
Content-Type: application/json
Content-Length: 128
Connection: close

{"users":[{"email":"john.doe@example.com","id":1,"name":"John Doe"},{"email":"jane.doe@example.com","id":2,"name":"Jane Doe"}]}
```