import socket
import requests


def get_location(ip_address):
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    print(response)
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name"),
        'country_code_iso3': response.get('country_code_iso3'),
        'value': 1
    }
    return location_data