import requests
import xmltodict

from models import User
from repositories import LoginFailedException


class ConventusAPI:

    def __init__(self, apikey, foreningsid):
        self._apikey = apikey
        self._foreningsid = foreningsid

    def login(self, email, password):
        url = f"https://www.conventus.dk/dataudv/api/medlemslogin/login.php"
        r = requests.post(url, data=dict(
            log_ind_med="email",
            email=email,
            adgangskode=password,
            foreningsid=self._foreningsid
        )).json()
        if not r["result"] == "success":
            raise LoginFailedException(r["result"])

        _id = r["profil"]["id"]
        return self.get_user(_id)

    def get_user(self, user_id: str) -> User:

        url = "https://www.conventus.dk/dataudv/api/adressebog/get_medlem.php"
        r = requests.get(url, params=dict(
            forening=self._foreningsid,
            key=self._apikey,
            id=user_id,
            relationer="true"
        ))

        medlem = xmltodict.parse(r.text)["conventus"]["medlem"]

        navn = medlem["navn"]
        medlem_groups = medlem["relationer"]["medlem"]["gruppe"]
        group_ids = [x["id"] for x in self._get_groups()]
        intersection = list(set(medlem_groups) & set(group_ids))
        is_active = len(intersection) > 0

        return User(user_id, navn, is_active, False, False, False, source="conventus")

    def _get_groups(self):
        url = "https://www.conventus.dk/dataudv/api/adressebog/get_grupper.php"
        r = requests.get(url, params=dict(
            forening=self._foreningsid,
            key=self._apikey,
            afdeling="45085"
        ))
        return xmltodict.parse(r.text)["conventus"]["grupper"]["gruppe"]

