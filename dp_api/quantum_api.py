import requests

def get_quantum_numbers(api_key, length, data_type, block_size=None):
    # Base URL of the API
    API_URL = "https://api.quantumnumbers.anu.edu.au"

    # Prepare parameters
    params = {
        'length': length,
        'type': data_type
    }
    if block_size and data_type in ['hex8', 'hex16']:
        params['size'] = block_size

    # Headers including your API key
    headers = {'x-api-key': api_key}

    # Send GET request to the API
    response = requests.get(API_URL, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        print("\nAPI CALL USED\n")
        return response.json()
    else:
        return f"Error: {response.status_code}"