# Tests

## Authentication

Assumes `test:123` is valid credentials.

Without auth header:
```
curl 'http://localhost:8000/'
```

With correct auth:
```
curl 'http://localhost:8000/' -u 'test:123'
```

With incorrect auth:
```
curl 'http://localhost:8000/' -u 'test:wrong'
```

## curl

Simple POST request:
```
curl "[::]:8000" -i -d "test=123"
```

Upload file (multipart encoding):
```
curl "[::]:8000" -i -F "data=@tests/file.txt"
```


## TODO

- What happens when I upload a file larger than my RAM? Can I limit the DoS potential?
