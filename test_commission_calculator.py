
import unittest
from unittest.mock import MagicMock, patch
from receipt_app import app

class CommissionCalculatorTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        # No DB init needed for mocks

    @patch('receipt_app.database.get_db_connection')
    def test_get_commission_calculator(self, mock_get_db):
        # Setup mock for get_projects
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock get_projects query result
        # fetchall returns list of dict-like objects
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'name': 'Vishvam', 'total_plots': 100, 'plots_to_landowners': 10}
        ]
        
        with self.client.session_transaction() as sess:
            sess['username'] = 'test_admin'
            sess['role'] = 'admin'
            sess['user_id'] = 1
            sess['logged_in'] = True
            
        response = self.client.get('/commission_calculator')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Commission Calculator', response.data)
        # Verify Agent fields are NOT present in HTML
        self.assertNotIn(b'Agent Commission Rate', response.data)

    @patch('receipt_app.database.get_db_connection')
    def test_post_valid_commission(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock fetchone calls if any (e.g. user lookup during request?)
        # But we injected session so basic login lookup skipped. 
        # save_commission_to_db does INSERT.
        
        with self.client.session_transaction() as sess:
            sess['username'] = 'test_admin'
            sess['role'] = 'admin'
            sess['user_id'] = 1
            sess['logged_in'] = True

        data = {
            'plot_no': '101',
            'project_name': 'Vishvam',
            'sq_yards': '200',
            'original_price': '1000',
            'negotiated_price': '900',
            'advance_received': '5000',
            'agreement_percentage': '0.30', 
            'amount_paid_at_agreement': '20000',
            'amc_charges': '500',
            
            # Application uses list inputs
            'cgm_rate': '10', 
            'srgm_rate[]': '20',
            'gm_rate[]': '30',
            'dgm_rate[]': '40',
            'agm_rate[]': '50',
            
            'cgm_name': 'CGM User',
            'srgm_name[]': 'SrGM User',
            'gm_name[]': 'GM User',
            'dgm_name[]': 'DGM User',
            'agm_name[]': 'AGM User',
        }
        
        response = self.client.post('/commission_calculator', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify INSERT was called
        # We need to find the execute call that starts with INSERT INTO commissions
        insert_called = False
        for call in mock_cursor.execute.call_args_list:
            args, _ = call
            query = args[0]
            if "INSERT INTO commissions" in query:
                insert_called = True
                params = args[1]
                # Verify agm_rate is passed as 50.0
                # We added advance_received, so index changes. 
                # Let's inspect the query params broadly or index if we know column order.
                # Columns: ..., cgm_rate, srgm_rate, gm_rate, dgm_rate, agm_rate, ...
                # Let's verify 50.0 is present in params
                self.assertIn(50.0, params)
                self.assertIn(40.0, params) # DGM
                self.assertIn('AGM User', params)
                break
        
        self.assertTrue(insert_called, "INSERT INTO commissions query not found")

    @patch('receipt_app.database.get_db_connection')
    def test_post_with_ignored_agent_data(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        with self.client.session_transaction() as sess:
            sess['username'] = 'test_admin'
            sess['role'] = 'admin'
            sess['user_id'] = 1
            sess['logged_in'] = True

        data = {
            'plot_no': '102',
            'project_name': 'Vishvam',
            'sq_yards': '100',
            'original_price': '1000',
            'negotiated_price': '900',
            'advance_received': '5000',
            'agreement_percentage': '0.30',
            'amount_paid_at_agreement': '20000',
            'amc_charges': '500',
            'cgm_rate': '10', 
            'srgm_rate[]': '20', 
            'gm_rate[]': '30', 
            'dgm_rate[]': '40', 
            'agm_rate[]': '50',
            'cgm_name': 'CGM', 
            'srgm_name[]': 'SrGM', 
            'gm_name[]': 'GM', 
            'dgm_name[]': 'DGM', 
            'agm_name[]': 'AGM',
            
            # INJECT OLD AGENT DATA
            'agent_rate': '999.9',
            'agent_name': 'Ignored Agent',
            'agent_commission_rate': '5'
        }
        
        response = self.client.post('/commission_calculator', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify INSERT called and verify params
        for call in mock_cursor.execute.call_args_list:
            args, _ = call
            query = args[0]
            if "INSERT INTO commissions" in query:
                params = args[1]
                # Ensure agent data is NOT in params
                self.assertNotIn(999.9, params) # agent_rate
                self.assertNotIn('Ignored Agent', params)
                # Verify valid data is still there
                self.assertIn(50.0, params)

if __name__ == '__main__':
    unittest.main()
