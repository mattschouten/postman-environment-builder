import json
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

    def test_encodes_quotes(self):
        md = '''
            | Name | Literal Value            |
            ----------------
            | NAME | Double " single ' quotes |
        '''

        entries = postman_environment_builder.get_entries(md)

        vars = postman_environment_builder.entries_to_postman_variables(entries)

        output = postman_environment_builder.build_postman_environment("my env", vars).strip()

        parsed = json.loads(output);

        expected = {
            'id': 'my env',
            'name': 'my env',
            'values': [
                {
                    'key': 'NAME',
                    'value': 'Double " single \' quotes',
                    'enabled': True
                }
            ],
            '_postman_variable_scope': 'environment',
            '_postman_exported_using': 'Postman/7.36.1'
        }

        self.assertEqual(parsed, expected)
