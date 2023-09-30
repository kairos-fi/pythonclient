import requests
import os
import json
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256


BASE_URL = os.environ["KAIROS_API_URL"]
CLIENT_ID = os.environ["KAIROS_CLIENT_ID"]
CLIENT_SECRET = os.environ["KAIROS_CLIENT_SECRET"]
PRIVATE_KEY = os.environ["RSA_PRIVATE_KEY"]


def login():
    """Attempts a login to Kairos API using the client ID

    Returns
    -------
    str
        The encrypted challenge received as a base64 enconded str
    """
    payload = {"client_id": CLIENT_ID}
    url = '/'.join([BASE_URL, 'login'])
    print('Attempt login to:', url, '\n')
    print('With payload:', json.dumps(payload, indent=2), '\n')
    headers =  {"Content-Type":"application/json"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    json_response = response.json()

    return json_response['challenge']


def decrypt(challenge):
    """Decrypts the given base64 challenge using the private key

    Parameters
    ----------
    challenge : str
        Base64 encoded string with the challenge received after login
    
    Returns
    -------
    str
        The decrypted challenge as a UTF-8 encoded string
    """
    key = RSA.import_key(PRIVATE_KEY)
    cipher_rsa = PKCS1_OAEP.new(key, hashAlgo=SHA256)
    encrypted_challenge = base64.b64decode(challenge)
    decrypted_challenge = cipher_rsa.decrypt(encrypted_challenge)

    return decrypted_challenge.decode("utf-8")


def token(decrypted_challenge):
    """Request for an access token providing the decrypted challenge

    Parameters
    ----------
    decrypted_challenge : str
        UTF-8 encoded string with the decrypted challenge
    
    Returns
    -------
    str
        The one hour valid access token
    """
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "challenge": decrypted_challenge
    }
    url = '/'.join([BASE_URL, 'token'])
    print('Attempt to request a token:', url, '\n')
    print('With payload:', json.dumps(payload, indent=2), '\n')
    headers =  {"Content-Type":"application/json"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    json_response = response.json()

    return json_response["access_token"]

print('\n')
print('Kairos API usage example in Python')
print('----------------------------------', '\n')

# Perform the login
challenge = login()

# Decrypt the challenge
decrypted_challenge = decrypt(challenge)

# Ask for an access token
access_token = token(decrypted_challenge)

print('Here is your token:', access_token)
