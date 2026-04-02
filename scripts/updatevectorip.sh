# Le but de ce script est de résoudre l'adresse IPv4 de l'hôte "vector.local", de l'exporter en tant que variable d'environnement et de mettre à jour un fichier de configuration défini avec cette adresse IP. 

#!/usr/bin/env bash
set -euo pipefail

# Variables de configuration
VECTOR="vector.local"
ENV_VAR_NAME="VECTOR_IP"
# Use ANKI_SDK_CONFIG_DIR env var if set, otherwise default to /root/sdk_vector_config
SDK_CONFIG_DIR="${ANKI_SDK_CONFIG_DIR:-/root/sdk_vector_config}"
FILE_TO_UPDATE="${SDK_CONFIG_DIR}/sdk_config.ini"
SUBSTITUTION_FUNCTION='s/^(ip[[:space:]]*=[[:space:]]*).*/\1__IP__/'

is_ipv4() {
    local value="$1"
    [[ "$value" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]
}

resolve_host_ipv4() {
    local host="$1"
    local ip=""

    if command -v getent >/dev/null 2>&1; then
        ip=$(getent ahostsv4 "$host" 2>/dev/null | awk 'NR==1 {print $1}' || true)
        if is_ipv4 "$ip"; then
            echo "$ip"
            return 0
        fi
    fi

    if command -v avahi-resolve-host-name >/dev/null 2>&1; then
        ip=$(avahi-resolve-host-name "$host" 2>/dev/null | awk '{print $2}' | head -n 1 || true)
        if is_ipv4 "$ip"; then
            echo "$ip"
            return 0
        fi
    fi

    if command -v nslookup >/dev/null 2>&1; then
        ip=$(nslookup "$host" 2>/dev/null | awk '/^Address[[:space:]]*[: ]/{print $NF}' | grep -E '^([0-9]{1,3}\.){3}[0-9]{1,3}$' | head -n 1 || true)
        if is_ipv4 "$ip"; then
            echo "$ip"
            return 0
        fi
    fi

    if command -v ping >/dev/null 2>&1; then
        ip=$(ping -c 1 "$host" 2>/dev/null | sed -nE 's/.*\((([0-9]{1,3}\.){3}[0-9]{1,3})\).*/\1/p' | head -n 1 || true)
        if is_ipv4 "$ip"; then
            echo "$ip"
            return 0
        fi
    fi

    return 1
}

replace_json_ip() {
    local ip="$1"
    local file="$2"
    local tmp_file="${file}.tmp"
    local sed_expr

    sed_expr="${SUBSTITUTION_FUNCTION//__IP__/${ip}}"

    sed -E "$sed_expr" "$file" >"$tmp_file"
    mv "$tmp_file" "$file"
}

if ! IP=$(resolve_host_ipv4 "$VECTOR"); then
    echo "Erreur : impossible de resoudre l'IPv4 pour l'hote $VECTOR" >&2
    exit 1
fi

export "${ENV_VAR_NAME}=${IP}"

ENV_FILE="/etc/profile.d/${ENV_VAR_NAME,,}_env.sh"
if [[ -d "$(dirname "$ENV_FILE")" ]]; then
    printf 'export %s="%s"\n' "$ENV_VAR_NAME" "$IP" >"$ENV_FILE" || true
    chmod 0644 "$ENV_FILE" 2>/dev/null || true
fi

if [[ ! -f "$FILE_TO_UPDATE" ]]; then
    echo "Erreur : fichier introuvable $FILE_TO_UPDATE" >&2
    exit 1
fi

cp "$FILE_TO_UPDATE" "$(basename "$FILE_TO_UPDATE").backup"
replace_json_ip "$IP" "$FILE_TO_UPDATE"

echo "$VECTOR IPv4 address: $IP"
echo "File updated : $FILE_TO_UPDATE"
echo "Environment variable exported : $ENV_VAR_NAME"
echo "Backup file : $(basename "$FILE_TO_UPDATE").backup"


exit 0
