import requests
from rides import app

def send_join(to, join, ride):
    pings_enabled = app.config.get["PINGS_ENABLED"]
    pings_join_route = app.config.get["PINGS_JOIN_ROUTE_UUID"]
    pings_token = app.config.get["PINGS_TOKEN"]
    if pings_join_route is None or pings_join_route == "" or pings_token is None or pings_token == "" or not pings_enabled:
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
    pings_enabled = app.config.get["PINGS_ENABLED"]
    pings_leave_route = app.config.get["PINGS_LEAVE_ROUTE_UUID"]
    pings_token = app.config.get("PINGS_TOKEN")
    if pings_leave_route is None or pings_leave_route == "" or pings_token is None or pings_token == "" or not pings_enabled:
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
