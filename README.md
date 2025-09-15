# Client Python pour AzureAttestSKR

Client Python pour utiliser l'exécutable AzureAttestSKR (Azure Confidential Computing Secure Key Release) depuis votre code Python.

## Prérequis

- **Linux uniquement** (le programme vérifie automatiquement)
- Python 3.7+
- L'exécutable `AzureAttestSKR` dans le même répertoire que le script
- Accès sudo (requis par AzureAttestSKR)

## Installation

1. Téléchargez ce projet
2. Placez l'exécutable `AzureAttestSKR` dans le répertoire du projet
3. Rendez l'exécutable... exécutable : `chmod +x AzureAttestSKR`

Pour les tests unitaires :
```bash
pip install pytest
```

## Variables d'environnement

Le script utilise 4 variables d'environnement :

| Variable | Description | Exemple |
|----------|-------------|---------|
| `MAA_ENDPOINT` | URL du service d'attestation Azure | `https://sharedweu.weu.attest.azure.net` |
| `KEYVAULT_KEY` | URL complète de la clé Key Vault | `https://mykv.vault.azure.net/keys/mykey/version_GUID` |
| `KEY` | Clé secrète à chiffrer (pour wrap) | `mysecretkey123` |
| `KEY_ENCRYPTED` | Clé chiffrée à déchiffrer (pour unwrap) | `dGVzdC1lbmNyeXB0ZWQta2V5...` |

## Utilisation

### En ligne de commande

#### Chiffrer une clé (wrap)
```bash
export MAA_ENDPOINT="https://sharedweu.weu.attest.azure.net"
export KEYVAULT_KEY="https://mykv.vault.azure.net/keys/mykey/version_GUID"
export KEY="mysecretkey123"

python skr_client.py wrap
```

#### Déchiffrer une clé (unwrap)
```bash
export MAA_ENDPOINT="https://sharedweu.weu.attest.azure.net"
export KEYVAULT_KEY="https://mykv.vault.azure.net/keys/mykey/version_GUID"
export KEY_ENCRYPTED="<base64_from_previous_wrap>"

python skr_client.py unwrap
```

#### Mode debug
```bash
DEBUG=1 python skr_client.py wrap
```

### Intégration dans du code Python

```python
import os
from skr_client import SKRClient

# Configurer les variables d'environnement
os.environ["MAA_ENDPOINT"] = "https://sharedweu.weu.attest.azure.net"
os.environ["KEYVAULT_KEY"] = "https://mykv.vault.azure.net/keys/mykey/version_GUID"

# Pour chiffrer
os.environ["KEY"] = "mysecretkey123"
client = SKRClient(debug=True)
encrypted_key = client.wrap_key()
print(f"Clé chiffrée: {encrypted_key}")

# Pour déchiffrer
os.environ["KEY_ENCRYPTED"] = encrypted_key
client = SKRClient(debug=True)
decrypted_key = client.unwrap_key()
print(f"Clé déchiffrée: {decrypted_key}")
```

### Exemple complet cycle wrap/unwrap

```python
import os
from skr_client import SKRClient

def demo_secure_key_release():
    # Configuration
    os.environ.update({
        "MAA_ENDPOINT": "https://sharedweu.weu.attest.azure.net",
        "KEYVAULT_KEY": "https://mykv.vault.azure.net/keys/mykey/version_GUID",
        "KEY": "ma-cle-secrete-123"
    })
    
    client = SKRClient(debug=True)
    
    # 1. Chiffrer la clé
    print("=== CHIFFREMENT ===")
    encrypted = client.wrap_key()
    
    # 2. Sauvegarder/transmettre la clé chiffrée...
    
    # 3. Déchiffrer la clé
    print("\\n=== DÉCHIFFREMENT ===")
    os.environ["KEY_ENCRYPTED"] = encrypted
    decrypted = client.unwrap_key()
    
    # Vérification
    assert decrypted == "ma-cle-secrete-123"
    print("✓ Cycle complet réussi!")

if __name__ == "__main__":
    demo_secure_key_release()
```

## Tests

### Tests unitaires (avec mocks)

```bash
# Tests de base
pytest test_skr_client.py

# Mode verbose
pytest test_skr_client.py -v

# Avec logs debug
TEST_LOG_LEVEL=DEBUG pytest test_skr_client.py -v -s
```

### Tests d'intégration (exécution réelle)

⚠️ **Attention** : Ces tests appellent réellement l'exécutable AzureAttestSKR !

```bash
# Configurer l'environnement
export RUN_INTEGRATION=1
export MAA_ENDPOINT="https://your-maa-endpoint.attest.azure.net"
export KEYVAULT_KEY="https://your-keyvault.vault.azure.net/keys/your-key/version"
export KEY="test-secret-key"

# Placer l'exécutable AzureAttestSKR dans le répertoire

# Lancer les tests d'intégration
pytest test_skr_client.py -k integration -v
```

## Structure du projet

```
skr-python-tool/
├── skr_client.py           # Module principal
├── test_skr_client.py      # Tests unitaires
├── README.md              # Cette documentation
└── AzureAttestSKR         # Exécutable (à ajouter)
```

## Gestion d'erreurs

Le client gère plusieurs types d'erreurs :

- **RuntimeError** : Système non-Linux
- **ValueError** : Variables d'environnement manquantes
- **FileNotFoundError** : Exécutable AzureAttestSKR introuvable
- **PermissionError** : Exécutable non exécutable
- **subprocess.CalledProcessError** : Erreur lors de l'exécution d'AzureAttestSKR
- **subprocess.TimeoutExpired** : Timeout (120s par défaut)

## Sécurité

- Le script utilise `sudo` pour exécuter AzureAttestSKR (requis par le binaire)
- Les clés sont transmises via arguments de ligne de commande (visible dans `ps`)
- Mode debug : attention aux logs qui peuvent contenir des informations sensibles
- Ne pas commiter de clés secrètes dans le code source

## Logging

Le module utilise le module `logging` standard Python :

- **INFO** : Opérations principales (chiffrement/déchiffrement)
- **DEBUG** : Détails d'exécution, commandes, sorties
- **WARNING** : Messages stderr non-critiques
- **ERROR** : Erreurs d'exécution

Configuration du niveau :
```bash
# En ligne de commande
DEBUG=1 python skr_client.py wrap

# Dans les tests
TEST_LOG_LEVEL=DEBUG pytest test_skr_client.py -v -s
```

## Limitations

- Linux uniquement
- Nécessite sudo
- Timeout fixe de 120 secondes
- Exécutable doit être dans le même répertoire
- Pas de gestion de cache/persistance

## Références

- [Azure Confidential Computing CVM Guest Attestation](https://github.com/Azure/confidential-computing-cvm-guest-attestation)
- [Documentation AzureAttestSKR](https://github.com/Azure/confidential-computing-cvm-guest-attestation/blob/main/cvm-securekey-release-app/README.md)