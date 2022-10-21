import requests
from rides import app

def send_join(to, join, ride):
    if not app.config.get["PINGS_ENABLED"]:
        return
    pings_join_route = app.config.get["PINGS_JOIN_ROUTE_UUID"]
    pings_token = app.config.get["PINGS_TOKEN"]
    if not pings_join_route or not pings_token:
        print("Pings is not configured")
        return
    try:
        requests.post(
            f"https://pings.csh.rit.edu/service/route/{pings_join_route}/ping",
            json = {
                "username": to,
                "body": f"@{join} has joined \"{ride}\""
            },
            headers = {
                "Authorization": f"Bearer {pings_token}"
            }
        )
    except requests.exceptions.RequestException as e:
        print("Error sending ping")
        print(e)

def send_leave(to, leave, ride):
    if not app.config.get["PINGS_ENABLED"]:
        return
    pings_leave_route = app.config.get["PINGS_LEAVE_ROUTE_UUID"]
    pings_token = app.config.get("PINGS_TOKEN")
    if not pings_leave_route or not pings_token:
        print("Pings is not configured")
        return
    try:
        requests.post(
            f"https://pings.csh.rit.edu/service/route/{pings_leave_route}/ping",
            json = {
                "username": to,
                "body": f"@{leave} has left \"{ride}\""
            },
            headers = {
                "Authorization": f"Bearer {pings_token}"
            }
        )
    except requests.exceptions.RequestException as e:
        print("Error sending ping")
        print(e)
