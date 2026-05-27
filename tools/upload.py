import sys
import os
import time
import secrets
import requests
import jwt
import json

BASE_URL = 'https://addons.mozilla.org/api/v5/addons/'
TOKEN_EXPIRATION_TIME = 5  # minutes


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


def upload_create(file_path, headers):
    # upload the file
    with open(file_path, "rb") as f:
        response = requests.post(BASE_URL+"upload/",
                                 headers=headers,
                                 files={"upload": f},
                                 data={"channel": "unlisted"},
                                 timeout=10)

    # check response status
    if not response.ok:
        print(f"upload_create failed with {response.status_code}")
        print(response.text)
        sys.exit(response.status_code)

    # return uuid
    return json.loads(response.text)['uuid']


def upload_detail(uuid, headers):
    response = requests.post(BASE_URL+"upload/"+uuid,
                             headers=headers,
                             timeout=10)

    # check response status
    if not response.ok:
        print(f"upload_detail failed with {response.status_code}")
        print(response.text)
        sys.exit(response.status_code)

    return json.loads(response.text)


def version_create(uuid, add_on_id, headers):
    response = requests.post(BASE_URL+"addon/"+add_on_id+"/versions/",
                             headers=headers,
                             json={"upload": uuid},
                             timeout=10)

    # check response status
    if not response.ok:
        print(f"version_create failed with {response.status_code}")
        print(response.text)
        sys.exit(response.status_code)

    return json.loads(response.text)


add_on_id = sys.argv[1]
file_path = sys.argv[2]

headers = {
    "Authorization": "JWT "+generate_token(
        issuer=os.environ['JWT_ISSUER'],
        secret=os.environ['JWT_SECRET'])
}


# Upload
upload = upload_create(file_path, headers)
print("Uploaded "+upload)

# Wait for processing
print("Waiting for processing", end=" ", flush=True)
time.sleep(5)
detail = upload_detail(upload, headers)

while not detail['processed']:
    print(".", end="", flush=True)
    time.sleep(5)
    detail = upload_detail(upload, headers)

print(" done")

if not detail['valid']:
    print("Upload not valid, see upload_details.json", file=sys.stderr)

    with open("upload_details.json", "w", encoding="utf-8") as f:
        json.dump(detail, f, indent=4)

    sys.exit(1)

# Create version
version = version_create(upload, add_on_id, headers)

print(json.dumps(version, indent=2))
