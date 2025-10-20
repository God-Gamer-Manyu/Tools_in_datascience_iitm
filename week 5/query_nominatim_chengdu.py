import requests, sys

url = 'https://nominatim.openstreetmap.org/search'
params = {
    'format': 'json',
    'city': 'Chengdu',
    'country': 'China',
    'limit': 50,
}
headers = {
    'User-Agent': 'tools_in_datascience_godgamer@example.com (contact: your-email@example.com)'
}

resp = requests.get(url, params=params, headers=headers, timeout=15)
resp.raise_for_status()
data = resp.json()

# Search for osm_id that ends with '0264'
for item in data:
    osm_id = str(item.get('osm_id', ''))
    if osm_id.endswith('0264'):
        bbox = item.get('boundingbox')
        print('FOUND')
        print('osm_id:', osm_id)
        print('display_name:', item.get('display_name'))
        print('boundingbox:', bbox)
        # boundingbox is [south, north, west, east] or [south, north]?
        # Nominatim returns [south, north, west, east] sometimes as strings; typical is [south, north, west, east]
        # We'll print the maximum latitude (north / bbox[1])
        if bbox and len(bbox) >= 2:
            print('max_latitude:', bbox[1])
        sys.exit(0)

# If not found, print the top candidates for inspection
print('NOT FOUND: no osm_id ending with 0264')
for i, item in enumerate(data[:10]):
    print(i, item.get('osm_id'), item.get('display_name'))

sys.exit(1)
