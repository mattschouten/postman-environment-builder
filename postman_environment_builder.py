#!/usr/bin/env python3

import subprocess
import re
import extract_entries_from_markdown

def get_secret(key_name, vault_name):
    az_process = subprocess.Popen(['az', 'keyvault', 'secret', 'show', '--vault-name', vault_name, '-n', key_name], stdout=subprocess.PIPE)
    jq_process = subprocess.Popen(['jq', '-r', '.value'], stdin=az_process.stdout, stdout=subprocess.PIPE)
    out, err = jq_process.communicate()

    return out.decode('utf-8').strip()

def format_postman_variable(variable_name, value):
    return '{{"key": {}, "value": {}, "enabled": true }}'.format(variable_name, value)

def build_postman_environment(environment_name, entries):
    variables = ['\t\t' + format_postman_variable(k, v) for k,v in entries.items()]

    return '''
    {{
        "id": "{0}",
        "name": "{0}",
        "values": [
    {1}
        ],
        "_postman_variable_scope": "environment",
        "_postman_exported_using": "Postman/7.36.1"
    }}
    '''.format(environment_name, ',\n'.join(variables))

def get_entries(markdown=''):
    entries = extract_entries_from_markdown.table_to_rows(extract_entries_from_markdown.get_table_text(markdown))

    literals = []
    keyvault_entries = []

    if len(entries) > 0:
        name_key = 'Name'
        literal_key = 'Literal Value'
        kv_vault_name_key = 'Key Vault Name'
        kv_value_key = 'Key Vault Value'

        literals = [{'key': entry[name_key], 'value': entry[literal_key]} for entry in entries if literal_key in entry]
        keyvault_entries = [{'key': entry[name_key], 'key_name': entry[kv_value_key], 'vault_name': entry[kv_vault_name_key]} for entry in entries if kv_vault_name_key in entry]
    
    return {
        'literals': literals,
        'keyvault_entries': keyvault_entries
    }

if __name__ == '__main__':
    entries = {
        'user': 'APIACCESS',
        'password': get_secret(key_name='thePassword', vault_name='theKeyVaultName'),
        'url': 'hominsteadincsb-api.sabacloud.com'
    }

    print(build_postman_environment('MY ENV NAME', entries))
