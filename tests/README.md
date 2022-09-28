# Tests

For testing I call the program as follows:
```
./src/secure-upload-server --http-basic test 123 --gpg-symmetric TODO_CHANGE_ME
```

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

## GPG

`file.txt.gpg` is encrypted with symmetric password `TODO_CHANGE_ME`.
`wrong-pass.txt.gpg` is encrypted with the password `wrong`.

Upload file:
```
curl 'http://[::1]:8000/gpg' -u "test:123" -F "gpg=@tests/file.txt.gpg"
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
