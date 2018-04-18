import requests
from datetime import datetime


class HubStaff:
    def __init__(self, app_token: str):
        self.app_token = app_token
        self.auth_token = None
        self.user_id = None

    @classmethod
    def init_with_auth_token(cls, app_token: str, auth_token: str, user_id: str):
        hs = HubStaff(app_token)
        hs.auth_token = auth_token
        hs.user_id = user_id
        return hs

    def get_auth_headers(self) -> dict:
        return {
            'Auth-Token': self.auth_token,
            'App-Token': self.app_token
        }

    def auth(self, email: str, password: str):
        auth_response = requests.post(
            'https://api.hubstaff.com/v1/auth',
            data={
                'email': email,
                'password': password
            }, headers=self.get_auth_headers())
        auth_response.raise_for_status()
        self.auth_token = auth_response.json()['user']['auth_token']
        self.user_id = auth_response.json()['user']['id']

    def organizations_for_user(self, user_id: int):
        org_response = requests.get(
            'https://api.hubstaff.com/v1/users/{}/organizations'.format(
                user_id),
            headers=self.get_auth_headers()
        )
        org_response.raise_for_status()
        return org_response.json()

    def my_organizations(self):
        return self.organizations_for_user(self.user_id)

    def custom_by_date_team_report(
            self, start_date: datetime, end_date: datetime, organizations):
        response = requests.get(
            'https://api.hubstaff.com/v1/custom/by_date/team',
            params={
                'start_date': start_date.date().isoformat(),
                'end_date': end_date.date().isoformat(),
                'organizations': organizations
            }, headers=self.get_auth_headers())
        response.raise_for_status()
        return response.json()
