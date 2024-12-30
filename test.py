import requests

url = "http://127.0.0.1:5000/decrypt_text"
data = {
    "encrypted_text": "gAAAAABncO4cFOnTFDC1FyT2U01ctKfiodVs2nOGinoqgKtIpMgStRLwm2S2LACtRYmb1iwL71FAMizD1MGrDIjJY7Vn86_ycealmHt4so6D-HN4Xw-93ls="
}

response = requests.post(url, json=data)
print(response.json())