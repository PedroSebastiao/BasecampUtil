from basecampy3 import Basecamp3
from basecampy3 import config
from basecampy3.exc import NoDefaultConfigurationFound
from basecampy3.token_requestor import TokenRequester
from requests import Session

class APIWrapper(object):
    def __init__(self) -> None:
        self._api = None
        self.tokens = None
        self.session = Session()
        self.session.headers["User-Agent"] = "Basecamp App Rail Python Checkin Helper"
    
    def authenticate(self) -> bool:
        # try to load previously saved configuration
        try:
            loaded = self.load()
        except NoDefaultConfigurationFound as e:
            loaded = False
        if loaded:
            print('Loaded configuration from file.')
        else:
            redirect_uri = "http://localhost:33333"
            print(f'Please make sure you have an integration with redrect uri set to  "{redirect_uri}".')
            print('You can add one at "https://launchpad.37signals.com/integrations".')
            client_id = input("What is the intergration Client ID? ")
            client_secret = input("What is the intergration Client Secret? ")
            print('Proceeding to authenticate with:')
            print(f'  Client ID: {client_id}\n  Client Secret: {client_secret}\n  Redirect URI: {redirect_uri}')
            authenticated = self.authenticate_user(client_id, client_secret, redirect_uri)
            if not authenticated:
                print('Error authenticating.')
                return
            account = self.select_account()
            if account is None:
                print('Error selecting account.')
                return
            print('Saving configuration to file "basecamp.conf".')
            account_id = account['id']
            saved = self.save(client_id, client_secret, redirect_uri, account_id)
            if not saved:
                print('Error saving configuration.')



    def authenticate_user(self, client_id, client_secret, redirect_uri) -> bool:
        requester = TokenRequester(client_id, redirect_uri, self.session)
        code = requester.get_authorization()
        self.tokens = Basecamp3.trade_user_code_for_access_token(client_id, redirect_uri, client_secret, code, self.session)
        self._api = Basecamp3(access_token=self._access_token())
        return self.tokens is not None
    
    def _access_token(self) -> str:
        return self.tokens['access_token']

    @property
    def api(self) -> Basecamp3:
        return self._api


    # this function's code has been sourced from https://github.com/phistrom/basecampy3/blob/master/basecampy3/bc3_cli.py
    # The MIT License (MIT)
    # Copyright (c) 2018 Phillip Stromberg
    def select_account(self):
        accounts = [acct for acct in self.api.accounts]
        account = accounts[0] if len(accounts) == 1 else None

        if len(accounts) > 1:
            identity = self.api.who_am_i["identity"]
            while True:
                print("User ID %s, email %s has %s accounts. Which one do you want to use?" %
                        (identity["id"], identity["email_address"], len(accounts)))
                for idx, acct in enumerate(accounts, start=1):
                    print("%s) %s (ID = %s)" % (idx, acct["name"], acct["id"]))
                choice = input("Which of the above accounts do you want to use? ")
                try:
                    choice = abs(int(choice))
                    account = accounts[choice - 1]
                    print("Selected %(name)s (ID = %(id)s)" % acct)
                    break
                except (IndexError, TypeError, ValueError):
                    print("%s is not a valid choice. Please provide a number between 1 and %s" %
                            (choice, len(accounts)))
        
        return account
    
    def save(self, client_id, client_secret, redirect_uri, account_id) -> bool:
        conf = config.BasecampFileConfig(client_id=client_id, client_secret=client_secret,
                                            redirect_uri=redirect_uri, access_token=self.tokens['access_token'],
                                            refresh_token=self.tokens['refresh_token'], account_id=account_id)
        try:
            conf.save('basecamp.conf')
            return True
        except:
            return False
    
    def load(self) -> bool:
        conf = config.BasecampFileConfig.load_from_default_paths()
        self.tokens = {
            'access_token': conf.access_token,
            'refresh_token': conf.refresh_token
        }
        self._api = Basecamp3(conf=conf)
        return conf.is_usable and self.tokens is not None and self.api is not None