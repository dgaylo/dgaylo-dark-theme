import sys
import os
import time
import secrets
import requests
import jwt
import json

BASE_URL = 'https://addons.mozilla.org/api/v5/addons/'
POLL_PERIOD = 10 # seconds
TIME_OUT = 600 # 10 minutes, per Mozilla's own guidance

class Token:
    EXPIRATION_TIME = 5 * 60  # second

    def __init__(self, issuer, secret):
        self._issuer = issuer
        self._secret = secret
        self._value = self._create()

    def _create(self) -> str:
        issued_at_time = int(time.time())
        self._expiration_time = issued_at_time + self.EXPIRATION_TIME

        return jwt.encode(
            payload={
                "iss": self._issuer,
                "jti": secrets.token_hex(),
                "iat": issued_at_time,
                "exp": self._expiration_time
            },
            key=self._secret,
            algorithm="HS256"
        )

    @property
    def header(self) -> dict[str, str]:
        if int(time.time()) > self._expiration_time:
            self._value = self._create()

        return {"Authorization": "JWT "+self._value}


class Upload:
    def __init__(self, file_path, token: Token):
        self._token = token

        # upload the file
        with open(file_path, "rb") as f:
            response = requests.post(
                BASE_URL+"upload/",
                headers=self._token.header,
                files={"upload": f},
                data={"channel": "unlisted"},
                timeout=10,
                )

        # check response status
        if not response.ok:
            print(f"upload_create failed with {response.status_code}")
            print(response.text)
            sys.exit(response.status_code)

        # save UUID
        self.uuid = json.loads(response.text)['uuid']
        self._final_details = None

    def _get_details(self):
        response = requests.get(BASE_URL+"upload/"+self.uuid,
                                headers=self._token.header,
                                timeout=10)

        # check response status
        if not response.ok:
            print(f"upload_detail failed with {response.status_code}")
            print(response.text)
            sys.exit(response.status_code)

        return json.loads(response.text)

    @property
    def details(self):
        if self._final_details is None:
            # Wait for processing
            print("Waiting for processing", end=" ", flush=True)
            deadline = time.time() + TIME_OUT  
            while not (details := self._get_details())['processed']:
                if time.time() > deadline:
                    print("Timed out waiting for processing", file=sys.stderr)
                    sys.exit(1)
                print(".", end="", flush=True)
                time.sleep(POLL_PERIOD)
            print(" done")

            self._final_details = details

        return self._final_details


class Version:
    def __init__(self, upload: Upload, add_on_id, token: Token):
        self.add_on_id = add_on_id
        self._token = token

        # create the version
        response = requests.post(
            BASE_URL+"addon/"+self.add_on_id+"/versions/",
            headers=self._token.header,
            json={"upload": upload.uuid},
            timeout=10
        )

        # check response status
        if not response.ok:
            print(f"version_create failed with {response.status_code}")
            print(response.text)
            sys.exit(response.status_code)

        # save version number
        self.version_number = json.loads(response.text)["version"]
        self._file_info = None

    def _get_details(self):
        response = requests.get(
            BASE_URL + "addon/" + self.add_on_id + "/versions/" + self.version_number + "/",
            headers=self._token.header,
            timeout=10
        )

        if not response.ok:
            print(f"version_detail failed with {response.status_code}")
            print(response.text)
            sys.exit(response.status_code)

        return json.loads(response.text)

    @property
    def file_info(self):
        if self._file_info is None:
            # Wait for signing
            print("Waiting for signing", end=" ", flush=True)
            deadline = time.time() + TIME_OUT
            while not (file_info := self._get_details().get("file", {})).get("status") == "public":
                if time.time() > deadline:
                    print("Timed out waiting for signing", file=sys.stderr)
                    sys.exit(1)
                print(".", end="", flush=True)
                time.sleep(POLL_PERIOD)
            print(" done")

            self._file_info = file_info

        return self._file_info


add_on_id = sys.argv[1]
file_path = sys.argv[2]
output_path = sys.argv[3]

token = Token(
    issuer=os.environ['JWT_ISSUER'],
    secret=os.environ['JWT_SECRET']
    )


# Upload
upload = Upload(file_path, token)
print("Uploaded " + upload.uuid)

# Validate upload
if not upload.details['valid']:
    print("Upload not valid, see upload_details.json", file=sys.stderr)

    with open("upload_details.json", "w", encoding="utf-8") as f:
        json.dump(upload.details, f, indent=4)

    sys.exit(1)

# Create version
version = Version(upload, add_on_id, token)
print("Created version " + version.version_number)
download_url = version.file_info["url"]
print(download_url)

# Downloading
with requests.get(download_url, headers=token.header, stream=True, timeout=30) as r:
    r.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
