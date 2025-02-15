# backend/notifications.py
import requests

def send_push_notification(message, user_segment="All"):
    headers = {
        "Authorization": "Bearer YOUR_ONESIGNAL_API_KEY",  # Replace with your OneSignal API key
        "Content-Type": "application/json"
    }
    data = {
        "app_id": "YOUR_APP_ID",  # Replace with your OneSignal App ID
        "included_segments": [user_segment],
        "contents": {"en": message}
    }
    try:
        response = requests.post("https://onesignal.com/api/v1/notifications", json=data, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# For testing the notification function separately, run this file directly.
if __name__ == "__main__":
    result = send_push_notification("Test Notification: It's time to pray! 🙏")
    print("Notification sent:", result)
