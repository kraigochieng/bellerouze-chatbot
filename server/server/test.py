import requests

from server.settings import settings
from server.utils import get_text_message_input

url = f"https://graph.facebook.com/{settings.whatsapp_api_version}/{settings.whatsapp_phone_number_id}/messages"

headers = {
    "Authorization": "Bearer " + settings.whatsapp_access_token,
    "Content-Type": "application/json",
}

data = get_text_message_input(recipient="254792701195", text="data from backend")

response = requests.post(url, headers=headers, data=data)


print("Status Code:", response.status_code)
try:
    print("Response JSON:", response.json())
except Exception:
    print("Response Text:", response.text)
