import unittest
import PostmanEnvironmentBuilder.builder as postman_environment_builder

class TestPostmanEnvironmentBuilder(unittest.TestCase):

    def test_get_entries_returns_dictionary_with_empty_arrays_if_environment_table_not_found(self):
        entries = postman_environment_builder.get_entries()

        expected = {
            'literals': [],
            'keyvault_entries': []
        }
        self.assertEqual(entries, expected)

    def test_get_entries_returns_entry_for_literal_entry(self):
        md = '''
            | Name | Literal Value     |
            ----------------
            | NAME | Literally A Value |
        '''

        entries = postman_environment_builder.get_entries(md)

        expected = {
            'literals': [
                {
                    'key': 'NAME',
                    'value': 'Literally A Value'
                }
            ],
            'keyvault_entries': []
        }

        self.assertEqual(entries, expected)

    def test_get_entries_returns_entry_for_keyvault_entry(self):
        md = '''
            | Name | Key Vault Name    | Key Vault Value         |
            ----------------
            | Fred | Very Secure Vault | Third Box from the Left |
        '''

        entries = postman_environment_builder.get_entries(md)

        expected = {
            'literals': [],
            'keyvault_entries': [
                {
                    'key': 'Fred',
                    'vault_name': 'Very Secure Vault',
                    'key_name': 'Third Box from the Left'
                }
            ]
        }

        self.assertEqual(entries, expected)
