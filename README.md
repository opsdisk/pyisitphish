# isitphish API Client

A Python API client for interacting with the isitphish API (<https://www.isitphish.com/>).  Comments, suggestions, and
improvements are always welcome. Be sure to follow [@opsdisk](https://twitter.com/opsdisk) on Twitter for the latest
updates.

## Installation

```bash
git clone https://github.com/opsdisk/pyisitphish.git
cd pyisitphish
virtualenv -p python3.7 .venv  # If using a virtual environment.
source .venv/bin/activate  # If using a virtual environment.
pip install -r requirements.txt
```

## Update Credentials

If using a secrets file, create/update the `secrets.json` file with the host and API key.  See the usage section
on how to pass a secrets dictionary.

```bash
cp secrets_empty.json secrets.json
```

```json
{
    "isitphish": {
        "host": "api.isitphish.com",
        "token": "1234...abcd"
    }
}
```

## Usage

### Script

```bash
python isitphish.py -u https://phishbarrel.com
```

### Module

```python
import isitphish

# Pass a secrets file.
full_path_to_secrets_file_location="/home/user/secrets.json"

iip_client = isitphish.IsItPhishClient(secrets_file_location=full_path_to_secrets_file_location)
iip_client.retrieve_url_score("https://phishbarrel.com")

# Pass a secrets dictionary.
secrets_dict = {
    "isitphish": {
        "host": "api.isitphish.com",
        "token": "1234...abcd"
    }
}

iip_client = isitphish.IsItPhishClient(secrets_dict=secrets_dict)
iip_client.retrieve_url_score("https://phishbarrel.com")
```
