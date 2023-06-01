"""_summary_

    Returns:
        _type_: _description_
"""
import json
from cryptography.fernet import Fernet


class ConfigManager:
    """_summary_
    """    
    def __init__(self, path) -> None:
        self.path = path
        self.__config = {
            "reference_key": Fernet.generate_key().decode("utf-8"),
            "firebase_api_key": None,
            "email": None,
            "password": None,
        }
        
        try:
            with open(self.path, "x", encoding="utf-8"):
                pass
        except FileExistsError:
            self.__load_config()
            
    def get_firebase_api_key(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """        
        return self.__config["firebase_api_key"]
    
    def set_firebase_api_key(self, api_key: str):
        """_summary_

        Args:
            api_key (str): _description_
        """        
        self.__config["firebase_api_key"] = api_key
        self.__save_config()
    
    def get_login_credentials(self) -> dict:
        """_summary_

        Returns:
            dict: _description_
        """        
        return {
            'email': self.__config["email"],
            'password': self.__config["password"]
        }
           
    def set_login_credentials(self, email: str, password: str):
        """_summary_

        Args:
            email (str): _description_
            password (str): _description_
        """        
        self.__config["email"] = email
        self.__config["password"] = password
        self.__save_config()

    def __encrypt(self, data: str | None) -> str:
        return None if not data else Fernet(
            self.__config['reference_key'].encode()
            ).encrypt(
                data.encode()
            ).decode()

    def __decrypt(self, data: str | None) -> str:
        return None if not data else Fernet(
            self.__config['reference_key'].encode()
            ).decrypt(
                data.encode()
            ).decode()

    def __save_config(self):
        with open(self.path, "w", encoding="utf-8") as config_file:
            config = self.__config.copy()
            config["firebase_api_key"] = self.__encrypt(
                self.__config["firebase_api_key"])

            config["email"] = self.__encrypt(
                self.__config["email"])

            config["password"] = self.__encrypt(
                self.__config["password"])

            json.dump(config, config_file, indent=4)

    def __load_config(self):
        with open(self.path, "r", encoding="utf-8") as config_file:
            self.__config = json.load(config_file)
            self.__config["firebase_api_key"] = self.__decrypt(
                self.__config["firebase_api_key"])

            self.__config["email"] = self.__decrypt(
                self.__config["email"])

            self.__config["password"] = self.__decrypt(
                self.__config["password"])

            return self.__config