# Class to create, query, and extract data from United Power's web site


class UnitedPowerUsage:
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password