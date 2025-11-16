import requests

access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlNDJhMmQxYy0zNGNhLTQ4ZjYtYWI2NC0wNzY2OWU0OWJhMGQiLCJyb2xlIjoic3RyaW5nIiwiZXhwIjoxNzYzMzA4OTI3fQ._B_eDSRPKmDVrIiXXN-B6E12KKmwT_yanX6GK7c9I10"

url = "http://127.0.0.1:8000/auth/me"
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.post(url, headers=headers)  # atau GET, sesuai definisi endpoint
print(response.json())