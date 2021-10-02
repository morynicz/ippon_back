import os
import random

from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa

TEMPLATE = """
#!/bin/bash

export SECRET_KEY='{key}'
export DB_NAME='{dbname}'
export DB_USER='{dbuser}'
export DB_PASSWORD='{dbpass}'
export DB_HOST='localhost'
export DB_PORT=''
export SECRET_KEY_PRIVATE=`cat {keypath}/id_rsa`
export SECRET_KEY_PUBLIC=`cat {keypath}/id_rsa.pub`
export MAIL_USER=''
export MAIL_PASSWORD=''
export MAIL_HOST=''
export MAIL_PORT=''
export MAIL_USE_TLS='True'
export MAIL_USE_SSL=''
export MAIL_SSL_KEYFILE=''
export MAIL_SSL_CERTFILE=''
export ALLOWED_HOSTS='["localhost"]'
"""


def gen_ssh(dir):
    key = rsa.generate_private_key(backend=crypto_default_backend(), public_exponent=65537, key_size=2048)
    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption(),
    )
    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.OpenSSH, crypto_serialization.PublicFormat.OpenSSH
    )

    with open(os.path.join(dir, "id_rsa"), "wb") as private:
        private.write(private_key)

    with open(os.path.join(dir, "id_rsa.pub"), "wb") as public:
        public.write(public_key)


def gen_key():
    return "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)])


def generate():
    with open("secrets2.sh", "w") as file:
        dir = os.path.join(os.getcwd(), "keys")
        if not os.path.exists(dir):
            os.mkdir(dir)
        gen_ssh(dir)
        file.write(
            TEMPLATE.format(
                key=gen_key(),
                dbname="dbname",
                dbuser="dbuser",
                dbpass="dbpass",
                keypath=dir,
            )
        )


if __name__ == "__main__":
    generate()
