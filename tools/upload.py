#!/usr/bin/env python3
import sys
import time
import secrets
import requests
import jwt

BASE_URL = 'https://addons.mozilla.org/api/v4/'
ADD_ON_GUID = '{1e413e83-d695-419b-a0e9-8d9274959fc9}'
TOKEN_EXPIRATION_TIME = 1 # minutes


def generate_token(issuer, secret):
    """Get JWT Token"""

    issued_at_time = int(time.time())
    expiration_time = issued_at_time + 60 * TOKEN_EXPIRATION_TIME
    jwt_id = secrets.token_hex()

    payload = {
        "iss": issuer,
        "jti": jwt_id,
        "iat": issued_at_time,
        "exp": expiration_time
    }

    return jwt.encode(payload, secret, algorithm="HS256")


headers = {
    "Authorization": "JWT "+generate_token(sys.argv[1], sys.argv[2])
}

url = BASE_URL+"addons/"+ADD_ON_GUID+"/versions/"+sys.argv[3]+"/"


with open(sys.argv[4], 'rb') as fobj:
    response = requests.put(url, headers=headers, files={'upload': fobj})
    print(response.text)
