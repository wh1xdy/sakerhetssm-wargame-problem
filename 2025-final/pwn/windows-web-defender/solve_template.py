import requests

url = "http://127.0.0.1:50000/chall"

# make sure u dont lose this ...
session = requests.Session()

response = session.get(url)
print(response.text)

session.close()