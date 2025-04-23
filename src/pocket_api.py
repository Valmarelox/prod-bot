from requests import Session


class PocketAPI:
    def __init__(self, consumer_key, access_token):
        self._pocket = Session()
        self._pocket.headers.update({
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        })
        self._id_params = {
            'consumer_key': consumer_key,
            'access_token': access_token
        }
        self._pocket.base_url = "https://getpocket.com/v3/"

    def get(self, offset=0, **kwargs):
        params = {
            'offset': offset,
            'total': 1,
            **self._id_params,
            **kwargs
        }
        response = self._pocket.post(self._pocket.base_url + 'get', data=params)
        response.raise_for_status()
        return response.json()