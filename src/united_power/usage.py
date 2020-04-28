# Class to create, query, and extract data from United Power's web site


class UnitedPowerUsage:
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password

        # Set last billing year and current billing month usage
        # Values will be all columns pulled from CSV export file
        self.billing_year_usage = {}
        self.current_month_usage = {}

    
    def load_billing_year(self):
        """Create selenium session to website, download last years usage data by billing date"""

