import requests
import base64
import sys

PROJECT_KEY = None
ACCESS_TOKEN = None
CLIENT_ID = None
CLIENT_SECRET = None
HEADERS = None
BASE_URL = None

ENDPOINTS = [
    "products",
    "product-selections",
    "stores",
    "categories",
    "shipping-methods",
    "tax-categories",
    "product-types",
    "zones",
    "channels"
]

def get_auth_token():
    url = f"https://auth.us-central1.gcp.commercetools.com/oauth/token?grant_type=client_credentials"
    basic_auth = f"{CLIENT_ID}:{CLIENT_SECRET}"
    basic_auth = base64.b64encode(basic_auth.encode("utf-8")).decode("utf-8")

    payload = ""
    headers = {
            'Authorization': f"Basic {basic_auth}",
            }

    response = requests.request("POST", url, headers=headers, data=payload)   

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Failed to get access token: {response.status_code} - {response.text}")
        sys.exit(1)

def get_ids(endpoint):
    response = requests.get(f"{BASE_URL}/{endpoint}", headers=HEADERS)
    if response.status_code == 404:
        print(f"Endpoint {endpoint} empty. Skipping.")
        return []

    items = response.json()

    return [(item['id'], item['version']) for item in items['results'] if 'id' in item and 'version' in item]


def delete_item(endpoint, ids):
    url = f"{BASE_URL}/{endpoint}/{ids[0]}?version={ids[1]}"
    response = requests.delete(url, headers=HEADERS)
    
    if response.status_code == 404:
        print(f"Item {ids[0]} not found in {endpoint}. Skipping.")
    elif response.status_code == 400:
        handle_400_error(endpoint, ids, response.json())
    elif response.ok:
        print(f"Successfully deleted {ids[0]} from {endpoint}.")
    else:
        print(f"Unexpected error: {response.status_code} - {response.text}")

def handle_400_error(endpoint, ids, error_response):
    if 'errors' in error_response:
        for error in error_response['errors']:
            if error['code'] == "ReferenceExists":
                reference_type = error.get('referencedBy')
                print(f"Handling reference for {ids} in {endpoint} due to dependency on {reference_type}.")

                reference_type = f"{reference_type}s"

                if reference_type in ENDPOINTS:
                    handle_reference(reference_type, ids)
                
                print(f"Retrying delete for {ids} on {endpoint}.")
                delete_item(endpoint, ids)
                return

def handle_reference(reference_type, ids):
    id_list = get_ids(reference_type)
    for ids in id_list:
        delete_item(reference_type, ids)
    print(f"Deleted {reference_type} references for {ids[0]}.")

def main():
    for endpoint in ENDPOINTS:
        print(f"Clearing endpoint: {endpoint}")
        item_ids = get_ids(endpoint)
        for ids in item_ids:
            delete_item(endpoint, ids)

if __name__ == "__main__":
    if len(sys.argv) != 4:
       print("Usage: python reset_commercetools.py <PROJECT_KEY> <CLIENT_ID> <CLIENT_SECRET>")
       sys.exit(1)
    
    PROJECT_KEY = sys.argv[1]
    CLIENT_ID = sys.argv[2]
    CLIENT_SECRET = sys.argv[3]
    
    ACCESS_TOKEN = get_auth_token()

    HEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    BASE_URL = f"https://api.us-central1.gcp.commercetools.com/{PROJECT_KEY}"
    main()


