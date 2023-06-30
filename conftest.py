import pytest
from tools import RequestsTools


@pytest.fixture(scope='function', autouse=True)
def clean_records():
    """
    Fixture to clean all records in the DB except those not created by me
    before each test.
    """

    rt = RequestsTools()
    response = rt.client_get()
    json_data = response.json()
    ids = ['MBGA2UNLSCA2npxWArPdCw', 'QGVdjyceQHe6vLmjIOAOgw']
    for data in json_data['list']:
        if data['id'] not in ids:

            rt.clean_range(range_id=data['id'])