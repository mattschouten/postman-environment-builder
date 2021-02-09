#!/usr/bin/env bash
set -euo pipefail

# Usage:  create-postman-environment <Environment Name>
# e.g. create-postman-environment "Secret Stuff - PROD"
# You must be 'az login'd and have your subscription set if needed

function getSecret {
    local keyname=$1
    local vaultname=$2

    az keyvault secret show --vault-name ${vaultname} -n $keyname | jq -r .value
}

env_name="$1"
declare -A entries
entries["user"]="APIACCESS"
entries["password"]="$(getSecret thePassword theKeyVaultName)"
entries["url"]="hominsteadincsb-api.sabacloud.com"

declare -a entry_strings
for KEY in "${!entries[@]}"; do
    entry_strings+=(",\t\t{\"key\": \"${KEY}\", \"value\": \"${entries[$KEY]}\", \"enabled\": true }")
done
printf -v out '%s' "${entry_strings[@]}"

cat <<JSONHEAD
{
	"id": "${env_name}",
	"name": "${env_name}",
	"values": [
JSONHEAD

echo -e ${out:1}

cat <<JSONFOOT
	],
	"_postman_variable_scope": "environment",
	"_postman_exported_using": "Postman/7.36.1"
}
JSONFOOT
