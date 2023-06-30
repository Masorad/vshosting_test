"""
!!!!   README   !!!!

Some of many possible test scenarios for documented API:
https://docs.google.com/document/d/1Ozj7EGjgDxanLLF-Occ51cXpEpJH0UG_aQS08S6u4f8/edit?pli=1#heading=h.gpn5mnw15akb


various scenarios could be added for each endpoints such as:
More PUT negative scenarios could be added as they are quite similar to POST.
All input parameters required/not required could be verified
More technical validations and business validations

Please follow TODOs for findings
To run tests with parameters please run the whole class or
    set @enable_parametrized_tests(run_tests_with_default_values_only=True)

Cleaning fixture in -> conftetst.py
"""

from tools import RequestsTools, Ignored
from parameters_tools import enable_parametrized_tests, with_parameters


@enable_parametrized_tests(run_tests_with_default_values_only=False)
class TestHappyPath(RequestsTools):
    def test_get_range(self):
        """
        Get list and records by id
        Assert existing records
        """
        # batch
        response = self.client_get()

        # per id
        records = []
        json_data = response.json()
        for data in json_data['list']:
            records.append(self.client_get(range_id=data['id']).text)

        expected_response = {'list': [
            {'id': 'MBGA2UNLSCA2npxWArPdCw',
             'name': 'Address 1 1687421747096721703',
             'rangeCidr': '10.0.0.0/24',
             'gatewayIp': '10.0.0.5',
             'reservedIps': [],
             'created': '2023-06-22T08:15:47Z',
             'updated': '2023-06-22T08:15:47Z'},
            {'id': 'QGVdjyceQHe6vLmjIOAOgw',
             'name': 'Address 2',
             'rangeCidr': '172.0.0.0/24',
             'gatewayIp': '172.0.0.5',
             'reservedIps': ['172.0.0.6', '172.0.0.4'],
             'created': '2023-06-22T08:15:39Z',
             'updated': '2023-06-22T08:15:39Z'}]}
        # TODO "lastUpdate" defined in GET specification but "updated" received

        # records received in batch
        assert response.json() == expected_response

        # records received per id
        assert json_data == expected_response

    def test_post_single_range_and_delete(self):
        """
        Post a new ipv4 range, check if added and clean the data after the test

        """
        data = {'name': 'Test Address 1',
                'rangeCidr': '185.59.211.0/24',
                'gatewayIp': '185.59.211.1',
                'reservedIps': ['185.59.211.14', '185.59.211.15']}

        # add new ipv4 range
        post_response = self.client_post(data=data)
        range_id = post_response.json()['id']

        # check if range was uploaded
        get_response = self.client_get(range_id)

        # delete range
        delete_response = self.clean_range(range_id=range_id)

        # check if the range was deleted
        check_after_delete = self.client_get(range_id)

        expected_get_response = {'id': range_id,
                                 'name': 'Test Address 1',
                                 'rangeCidr': '185.59.211.0/24',
                                 'gatewayIp': '185.59.211.1',
                                 'reservedIps': ['185.59.211.14', '185.59.211.15'],
                                 'created': Ignored(),
                                 'updated': Ignored()}
        # TODO "lastUpdate" defined in POST specification but "updated" received

        expected_after_delete_message = '{"error":{"code":"ipv4RangeNotFound","message":"ipv4Range not found"}}'

        assert post_response.status_code == 200
        assert get_response.json() == expected_get_response
        assert post_response.json() == expected_get_response
        assert delete_response.text == '{"success":true}'
        assert check_after_delete.text == expected_after_delete_message

    def test_update_range(self):
        """
        Update already existing range using PUT - no reserved ips

        """
        data = {'name': 'Test Address 1',
                'rangeCidr': '185.59.211.0/24',
                'gatewayIp': '185.59.211.1',
                'reservedIps': ['185.59.211.14', '185.59.211.15']}

        # add new ipv4 range
        post_response = self.client_post(data=data)
        range_id = post_response.json()['id']

        new_data = {'name': 'Test Address 1',
                    'rangeCidr': '185.59.211.0/24',
                    'gatewayIp': '185.59.211.2'}
        put_response = self.client_put(data=new_data, range_id=range_id)

        # TODO "ipv4Range reservedIPs should not be required - test fails
        assert put_response.text != ('{"error":{"code":"badRequest","message":"invalid user input","meta":[{"parameter"'
                                     ':"reservedIps","message":"field is required","code":100}]}}')

    def test_update_received_ips(self):
        """
        Update already existing range using PUT

        """
        data = {'name': 'Test Address 1',
                'rangeCidr': '185.59.211.0/24',
                'gatewayIp': '185.59.211.1',
                'reservedIps': ['185.59.211.14', '185.59.211.15']}

        # add new ipv4 range
        post_response = self.client_post(data=data)
        range_id = post_response.json()['id']

        new_data = {'name': 'Test Address 1',
                    'rangeCidr': '185.59.211.0/24',
                    'gatewayIp': '185.59.211.1',
                    'reservedIps': ['185.59.211.10', '185.59.211.16']}
        put_response = self.client_put(data=new_data, range_id=range_id)

        # TODO "ipv4Range not found" doesn't seem like correct response to me. Successful update expected. - test fails
        assert put_response.text != '{"error":{"code":"ipv4RangeNotFound","message":"ipv4Range not found"}}'


@enable_parametrized_tests()
class TestNegativeScenarios(RequestsTools):
    """
    Negative test scenarios

    """

    def test_post_invalid_range(self):
        data = {'name': 'Test Address 1',
                'rangeCidr': '185.59.211.0/256',
                'gatewayIp': '185.59.211.1',
                'reservedIps': ['185.59.211.14', '185.59.211.15']}

        # add new ipv4 range
        post_response = self.client_post(data=data)
        assert post_response.status_code == 400
        assert post_response.text == '{"error":{"code":"invalidRange","message":"invalid range"}}'

    @with_parameters(gateway=['xxx', '185.59.211.256', None, ''])
    def test_post_invalid_gateway(self, gateway=None):
        data = {'name': 'Test Address 1',
                'rangeCidr': '185.59.211.0/24',
                'gatewayIp': gateway,
                'reservedIps': ['185.59.211.14', '185.59.211.15']}

        post_response = self.client_post(data=data)

        assert post_response.status_code == 400
        if gateway is None:
            assert post_response.text == ('{"error":{"code":"badRequest","message":"invalid user input","meta":['
                                          '{"parameter":"gatewayIp","message":"field is required","code":100}]}}')
        elif gateway == '':
            assert post_response.text == ('{"error":{"code":"badRequest","message":"invalid user input","meta":[{"'
                                          'parameter":"gatewayIp","message":"value should not be empty","code":100}]}}')
        else:
            assert post_response.text == '{"error":{"code":"invalidGateway","message":"invalid gateway"}}'

    def test_post_reserved_ips_out_of_range(self):
        data = {'name': 'Test Address 1',
                'rangeCidr': '185.59.211.0/24',
                'gatewayIp': '185.59.211.1',
                'reservedIps': ['10.0.0.5', '185.59.211.11']}

        post_response = self.client_post(data=data)
        json_response = post_response.json()

        if post_response.status_code == 200:
            range_id = json_response['id']
            self.clean_range(range_id=range_id)
        assert post_response.status_code == 400
        assert post_response.text == ('{"error":{"code":"reservedAddressOutOfRange",'
                                      '"message":"reserved address out of range"}}')

    def test_post_reserved_ips_collides_with_gateway(self):
        data = {'name': 'Test Address 1',
                'rangeCidr': '185.59.211.0/24',
                'gatewayIp': '185.59.211.1',
                'reservedIps': ['185.59.211.1', '185.59.211.14']}

        post_response = self.client_post(data=data)
        assert post_response.status_code == 400
        assert post_response.text == ('{"error":{"code":"reservedAddressCollideGateway","message":"reserved address '
                                      'collide with gateway"}}')

    @with_parameters(reserved_ips=['xxx', None, ''])
    def test_post_invalid_reserved_ips(self, reserved_ips=''):
        data = {'name': 'Test Address 1',
                'rangeCidr': '185.59.211.0/24',
                'gatewayIp': '185.59.211.1',
                'reservedIps': [reserved_ips]}

        post_response = self.client_post(data=data)

        assert post_response.status_code == 400
        assert post_response.text == '{"error":{"code":"invalidReservedAddress","message":"invalid reserved address"}}'

    def test_post_required_reserved_ips(self):
        """
        Negative scenario:
            reservedIps should not be required, however error message "field is required" is returned
        """
        data = {'name': 'Test Address 1',
                'rangeCidr': '185.59.211.0/24',
                'gatewayIp': '185.59.211.1'}
        response = self.client_post(data=data)

        unsuccessful_message = ('{"error":{"code":"badRequest","message":"invalid user input","meta":[{"parameter":'
                                '"reservedIPs","message":"field is required","code":100}]}}')
        assert response.text == unsuccessful_message  # TODO see test description
        assert response.status_code == 400

    def test_post_extra_parameter(self):
        """

        """
        data = {'name': 'Test Address 1',
                'rangeCidr': '185.59.211.0/24',
                'gatewayIp': '185.59.211.1',
                'some_field': 'test',
                'reservedIps': ['185.59.211.14', '185.59.211.15']}

        # add new ipv4 range
        post_response = self.client_post(data=data)
        range_id = post_response.json()['id']

        # check if range was uploaded
        get_response = self.client_get(range_id)

        assert 'some_field' not in get_response.text

    def test_double_post(self):
        """
        Adding already existing range should not be possible

        """
        data = {'name': 'Test Address 1',
                'rangeCidr': '185.59.211.0/24',
                'gatewayIp': '185.59.211.1',
                'reservedIps': ['185.59.211.14', '185.59.211.15']}

        # add new ipv4 range
        post_response = self.client_post(data=data)
        range_id = post_response.json()['id']

        # check if range was uploaded
        get_response = self.client_get(range_id)
        json_data = get_response.json()

        post_response = self.client_post(data=data)

        # delete range
        self.clean_range(range_id=range_id)
        assert json_data['name'] == 'Test Address 1'
        assert post_response.text == '{"error":{"code":"rangeNameAlreadyExists","message":"range name already exists"}}'

    @with_parameters(invalid_id=['tooshortid', 'toolooooooooooooooooooooong'])
    def test_delete_invalid_length(self, invalid_id='tooshortid'):
        response = self.client_get(invalid_id)

        assert response.text == ('{"error":{"code":"badRequest","message":"invalid user input","meta":'
                                 '[{"parameter":"id","message":"value should have 22 characters","code":100}]}}')
        assert response.status_code == 400

    @with_parameters(invalid_id=[None, ''])
    def test_delete_none(self, invalid_id=''):
        """
        delete None returns success
        """
        response = self.client_get(invalid_id)

        assert response.status_code == 200
        # TODO also returns a record with ip range which si unexpected

    def test_delete_non_existing_id(self):
        """
        delete non-existing id
        """
        response = self.client_get('22characterslongid0000')

        assert response.text == '{"error":{"code":"ipv4RangeNotFound","message":"ipv4Range not found"}}'
