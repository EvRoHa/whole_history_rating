import json

from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class dbSession(object):
    headers = {'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'}
    base_url = 'https://api.collegefootballdata.com'

    @staticmethod
    def requests_retry_session(retries=10, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None,
                               headers=None):
        if not headers:
            headers = dbSession.headers
        session = session or Session()
        session.headers = headers
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    @staticmethod
    def query_plays(url=base_url + '/plays', **kwargs):
        if len(kwargs.keys()) > 0:
            url = ''.join([url, '?', '&'.join([str(x) + '=' + str(kwargs[x]) for x in kwargs])])
        return json.loads(dbSession.requests_retry_session().get(url).text)

    @staticmethod
    def query_games(url=base_url + '/games', **kwargs):
        if len(kwargs.keys()) > 0:
            url = ''.join([url, '?', '&'.join([str(x) + '=' + str(kwargs[x]) for x in kwargs])])
        return json.loads(dbSession.requests_retry_session().get(url).text)

    @staticmethod
    def query_teams(url=base_url + '/teams', **kwargs):
        if len(kwargs.keys()) > 0:
            url = ''.join([url, '?', '&'.join([str(x) + '=' + str(kwargs[x]) for x in kwargs])])
        return json.loads(dbSession.requests_retry_session().get(url).text)
