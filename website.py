import socket
import requests

def get_ip_address(hostname):
    return socket.gethostbyname(hostname)


def get_location(hostname):
    ip_address = get_ip_address(hostname)
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name")
    }
    return location_data