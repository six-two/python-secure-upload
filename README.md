# secure-upload

[![PyPI version](https://img.shields.io/pypi/v/secure-upload)](https://pypi.org/project/secure-upload/)
![License](https://img.shields.io/pypi/l/secure-upload)
![Python versions](https://img.shields.io/pypi/pyversions/secure-upload)

This is intended to be a tool to securely and easily transfer files from one computer to another.
While there are already many other packages for this purpose, this should offer the follwoing features:

- All transfers should be protected, so that Man-in-the-Middle attackers can not read the data you transfer
- Uploads should be possible via a simple web interface or via command line
- Transfers are one way, nobody can see any files that were uploaded, except the server's owner (by checking the local file system)
- Clients should be authenticated before uploads are stored on the server, so thatan attacker can not fill up all available server space.
Ideally these tokens would also be safe against an MitM attacker.

## Planned transfer protocols

### HTTPS (recommended)

A standard web server that provides convidentiallity via TLS.
This should work both with the web interface and with command line tools (`curl`).
The disadvantage is, that the setup is non-trivial (buying a domain, setting up DNS records, obtaining TLS certificate, etc).

### HTTP, but encrypted via web interface

Encrypt in browser with a key derived from a shared secred (password) and decrypted on the sever.

### HTTP, but symetrically encrypted with GPG

Encrypted on the client via `gpg` with a symmetric cipher, and then decrypted on the server with `gpg`.
Like with the web interface the key should be derived from a shared secred (password).

## Notable changes

### Version 0.0.1

- Uploaded placeholder to secure the name on PyPI
