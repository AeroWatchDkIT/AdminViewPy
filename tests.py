import unittest
from unittest.mock import patch
from app import app  # Import your Flask app

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.context = app.app_context()  # Get an application context
        self.context.push()  # Push the context so the app thinks it's running


    def test_index_route(self):
        with patch('app.requests.get') as mocked_get:
            # Mock successful API responses for forklifts and users
            mocked_get.return_value.json.return_value = {'entities': [], 'users': []}
            mocked_get.return_value.status_code = 200
            
            response = self.app.get('/')
            self.assertEqual(response.status_code, 200)
            # Additional checks can be performed here based on the expected output

    def test_create_user_post(self):
        with patch('app.requests.post') as mocked_post, \
             patch('app.requests.get') as mocked_get:
            # Mock the POST request to return a successful creation status
            mocked_post.return_value.status_code = 201
            # Mock the GET request for fetching users data in the redirected index page
            mocked_get.return_value.json.return_value = {'users': []}
            mocked_get.return_value.status_code = 200
            
            data = {
                'id': '123',
                'userType': '1',
                'firstName': 'Test',
                'lastName': 'User',
                'passcode': 'pass123',
                'forkliftCertified': 'true',
                'incorrectPalletPlacements': '0'
            }
            response = self.app.post('/createUser', data=data, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            # Additional checks can be performed here based on the expected output

    def tearDown(self):
        self.context.pop()  # Pop the context at the end of the test

    # Add more tests for different scenarios and routes as necessary

if __name__ == '__main__':
    unittest.main()
