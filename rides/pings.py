import requests
from rides import app

def send_join(to, join, ride):
    pings_join_route = app.config["PINGS_JOIN_ROUTE"]
    pings_token = app.config.get["PINGS_TOKEN"]
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

def send_leave(to, leave, ride):
    pings_leave_route = app.config.get["PINGS_LEAVE_ROUTE"]
    pings_token = app.config.get("PINGS_TOKEN")
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
