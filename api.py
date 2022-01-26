from datetime import datetime

logins = {

}

tokens = {

}


USER = {
    "id": "erik",
    "name": "Erik Eriksen",
    "valid_to": datetime(2022, 10, 10),
    "s1": True,
    "s2": True,
    "s3": False
}


def do_login(username: str, password: str):

    logins[username] = USER

    return logins[username]
