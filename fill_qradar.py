import requests
import configparser
import query_ad

config = configparser.ConfigParser()
config.read('config.ini')

# QRadar API configuration
qradar_url = config.get('QRADAR', 'url')
qradar_url_endpoint = f'{qradar_url}/api/reference_data/sets'
api_key = config.get('QRADAR', 'api_key')
cert = config.get('QRADAR', 'certificate')


reference_set_id = config.get('QRADAR', 'ref_set')
data_to_add = query_ad.main()

def clean_reference_set():
    # Clean the reference set
    clean_url = f'{qradar_url_endpoint}/{reference_set_id}'
    headers = {'SEC': api_key}
    payload = {'purge_only': 'true'}
    response = requests.delete(clean_url, headers=headers, json=payload, verify=cert)

    if response.status_code == 200:
        print('Reference set cleaned successfully')
    else:
        print('Failed to clean reference set')
        print(response.text)

def fill_reference_set(data):
    # Fill the reference set with new data
    fill_url = f'{qradar_url_endpoint}/bulk_load/{reference_set_id}'
    headers = {'SEC': api_key}
    payload = {'data': data}
    response = requests.post(fill_url, headers=headers, json=payload, verify=cert)

    if response.status_code == 200:
        print('Reference set filled successfully')
    else:
        print('Failed to fill reference set')
        print(response.text)

def main():
    clean_reference_set()
    fill_reference_set(data_to_add)

if __name__ == "__main__":
    main()