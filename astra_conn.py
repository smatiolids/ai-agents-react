from urllib.parse import urlencode
import os
from astrapy import DataAPIClient


class AstraDBConnection:
    _instance = None

    astra_db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AstraDBConnection, cls).__new__(cls)
            cls._instance._init_connection()
        return cls._instance
    
    def _init_connection(self):
        print("Connecting to %s", os.getenv('ASTRA_DB_API_ENDPOINT'))
        self.astra_data_api = DataAPIClient(os.getenv('ASTRA_DB_APPLICATION_TOKEN'))
        self.astra_db = self.astra_data_api.get_database(os.getenv('ASTRA_DB_API_ENDPOINT'))

    def get_session(self):
        if self.astra_db == None:
            self._init_connection()
        return self.astra_db
