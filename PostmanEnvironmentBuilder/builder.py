#!/usr/bin/env python3

import sys
import subprocess
import re
#import extract_entries_from_markdown
import PostmanEnvironmentBuilder.extract_entries_from_markdown as extract_entries_from_markdown

def get_secret(key_name, vault_name):
    print("Looking up {0} from {1} using 'az keyvault secret show --vault-name \"{1}\" -n \"{0}\"'".format(key_name, vault_name))
    az_process = subprocess.Popen(['az', 'keyvault', 'secret', 'show', '--vault-name', vault_name, '-n', key_name], stdout=subprocess.PIPE)
    jq_process = subprocess.Popen(['jq', '-r', '.value'], stdin=az_process.stdout, stdout=subprocess.PIPE)
    out, err = jq_process.communicate()

    return out.decode('utf-8').strip()

def format_postman_variable(variable_name, value):
    return '{{"key": {}, "value": {}, "enabled": true }}'.format(variable_name, value)

def build_postman_environment(environment_name, postman_variables):
    variables = ['\t\t' + format_postman_variable(k, v) for k,v in postman_variables.items()]

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

def get_entries(markdown='', target_heading_text=''):
    entries = extract_entries_from_markdown.table_to_rows(extract_entries_from_markdown.get_table_text(markdown=markdown, target_heading_text=target_heading_text))

    literals = []
    keyvault_entries = []
    if len(entries) > 0:
        name_key = 'Name'
        literal_key = 'Literal Value'
        kv_vault_name_key = 'Key Vault Name'
        kv_value_key = 'Key Vault Value'

        literals = [{'key': entry[name_key], 'value': entry[literal_key]} for entry in entries if literal_key in entry]
        keyvault_entries = [{'key': entry[name_key], 'key_name': entry[kv_value_key], 'vault_name': entry[kv_vault_name_key]} \
                                                for entry in entries if kv_vault_name_key in entry and kv_value_key in entry]

    return {
        'literals': literals,
        'keyvault_entries': keyvault_entries
    }

def entries_to_postman_variables(entries):
    postman_variables = { literal_entry['key']: literal_entry['value'] for literal_entry in entries['literals'] }

    for kv_entry in entries['keyvault_entries']:
        postman_variables[kv_entry['key']] = get_secret(kv_entry['key_name'], kv_entry['vault_name'])

    return postman_variables

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:  \n\t{} <Markdown File> <Postman Collection Name> [Label in Markdown]\n'.format(sys.argv[0]))
        print('Example:  \n\t{} README.md "My API - DEV" "Postman Environment - API - Dev"\n'.format(sys.argv[0]))
        exit()

    markdown_filename = sys.argv[1]
    postman_collection_name = sys.argv[2]
    target_heading_text = sys.argv[3] if len(sys.argv) > 3 else None

    with open(markdown_filename) as f:
        markdown = f.read()

    entries = get_entries(markdown, target_heading_text)

    postman_variables = entries_to_postman_variables(entries)

    print(build_postman_environment(postman_collection_name, postman_variables))
