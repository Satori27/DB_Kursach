import requests
API_BASE_URL = "http://localhost:8000"  # Замените на реальный URL вашего API


# Функция для отправки запросов на API
def send_request(endpoint, method="POST", data=None, cookies=None):
    url = f"{API_BASE_URL}/{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if method == "POST":
        response = requests.post(url, json=data, headers=headers, cookies=cookies)
    elif method=="GET":
        response = requests.get(url, headers=headers, cookies=cookies)
        return response
    elif method=="PUT":
        response = requests.put(url, headers=headers, cookies=cookies)

    else:
        response = requests.patch(url, json=data, headers=headers, cookies=cookies)
    return response
