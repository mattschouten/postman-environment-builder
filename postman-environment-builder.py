#!/usr/bin/env python3

import subprocess

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

entries = {
    'user': 'APIACCESS',
    'password': get_secret(key_name='thePassword', vault_name='theKeyVaultName'),
    'url': 'hominsteadincsb-api.sabacloud.com'
}

print(build_postman_environment('MY ENV NAME', entries))
