import requests

url = "http://localhost:5000/get-lab-tests"
files = {'image': open('img4.png', 'rb')}
response = requests.post(url, files=files)

print(response.status_code)
print(response.json())