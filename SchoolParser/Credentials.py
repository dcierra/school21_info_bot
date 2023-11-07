import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


class GetCredentials:
    def __init__(self, auth_login: str, auth_password: str):
        self.auth_url = 'https://edu.21-school.ru'
        self.auth_login = auth_login
        self.auth_password = auth_password

    def get_school_id(self) -> str:
        cookies = {
            'tokenId': self.get_token_id()
        }

        json_data = {
            'operationName': 'userRoleLoaderGetRoles',
            'variables': {},
            'query': 'query userRoleLoaderGetRoles {\n  user {\n    getCurrentUser {\n      functionalRoles {\n        '
                     'code\n        __typename\n      }\n      id\n      studentRoles {\n        id\n        school {\n'
                     '          id\n          shortName\n          organizationType\n          __typename\n        }\n '
                     '       status\n        __typename\n      }\n      userSchoolPermissions {\n        schoolId\n    '
                     '    permissions\n        __typename\n      }\n      systemAdminRole {\n        id\n        '
                     '__typename\n      }\n      businessAdminRolesV2 {\n        id\n        school {\n          id\n  '
                     '        organizationType\n          __typename\n        }\n        orgUnitId\n       '
                     ' __typename\n      }\n      __typename\n    }\n    getCurrentUserSchoolRoles {\n      schoolId\n'
                     '      __typename\n    }\n    __typename\n  }\n}\n',
        }

        response = requests.post('https://edu.21-school.ru/services/graphql', cookies=cookies,
                                 json=json_data).json()

        return response['data']['user']['getCurrentUserSchoolRoles'][0]['schoolId']

    def get_token_id(self) -> str:
        if self.auth_login and self.auth_password:
            options = webdriver.ChromeOptions()
            options.add_argument('headless')

            driver = webdriver.Chrome(options=options)
            driver.get(self.auth_url)

            login = driver.find_element(By.NAME, 'username')
            password = driver.find_element(By.NAME, 'password')

            login.clear()
            password.clear()

            login.send_keys(self.auth_login)
            password.send_keys(self.auth_password)
            password.send_keys(Keys.ENTER)
            token_id = [cookie['value'] for cookie in driver.get_cookies()][-1]

            driver.close()
            return token_id
