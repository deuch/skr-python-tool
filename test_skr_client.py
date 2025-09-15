import os
import sys
import platform
import subprocess
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import logging

# Ajouter le répertoire parent au path pour importer skr_client
sys.path.insert(0, str(Path(__file__).parent))

import skr_client

# Configuration du logging pour les tests
log_level = os.environ.get("TEST_LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO), 
                   format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


class TestSKRClient:
    """Tests unitaires pour SKRClient."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        # Variables d'environnement de test
        self.test_env = {
            "MAA_ENDPOINT": "https://test.attest.azure.net",
            "KEYVAULT_KEY": "https://test.vault.azure.net/keys/testkey/version",
            "KEY": "test-secret-key-123",
            "KEY_ENCRYPTED": "dGVzdC1lbmNyeXB0ZWQta2V5LTEyMw=="
        }
    
    @patch.dict(os.environ, {"MAA_ENDPOINT": "https://test.attest.azure.net", 
                            "KEYVAULT_KEY": "https://test.vault.azure.net/keys/testkey/version"})
    @patch('skr_client.platform.system')
    def test_init_success(self, mock_platform):
        """Test d'initialisation réussie."""
        logger.info("=== Test initialisation réussie ===")
        mock_platform.return_value = "Linux"
        
        client = skr_client.SKRClient(debug=True)
        
        assert client.maa_endpoint == "https://test.attest.azure.net"
        assert client.keyvault_key == "https://test.vault.azure.net/keys/testkey/version"
        logger.info("✓ Initialisation réussie")
    
    @patch('skr_client.platform.system')
    def test_init_non_linux_fails(self, mock_platform):
        """Test échec sur système non-Linux."""
        logger.info("=== Test échec système non-Linux ===")
        mock_platform.return_value = "Windows"
        
        with pytest.raises(RuntimeError, match="ne fonctionne que sur Linux"):
            skr_client.SKRClient()
        logger.info("✓ Erreur Linux correctement levée")
    
    def test_init_missing_env_vars_fails(self):
        """Test échec avec variables d'environnement manquantes."""
        logger.info("=== Test variables d'environnement manquantes ===")
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('skr_client.platform.system', return_value="Linux"):
                with pytest.raises(ValueError, match="Variables d'environnement manquantes"):
                    skr_client.SKRClient()
        logger.info("✓ Erreur variables manquantes correctement levée")
    
    @patch.dict(os.environ, {"MAA_ENDPOINT": "https://test.attest.azure.net", 
                            "KEYVAULT_KEY": "https://test.vault.azure.net/keys/testkey/version",
                            "KEY": "test-secret-key"})
    @patch('skr_client.platform.system')
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    @patch('os.access')
    def test_wrap_key_success(self, mock_access, mock_exists, mock_subprocess, mock_platform):
        """Test chiffrement réussi."""
        logger.info("=== Test chiffrement réussi ===")
        
        # Setup mocks
        mock_platform.return_value = "Linux"
        mock_exists.return_value = True
        mock_access.return_value = True
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "dGVzdC1lbmNyeXB0ZWQta2V5"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        client = skr_client.SKRClient(debug=True)
        result = client.wrap_key()
        
        assert result == "dGVzdC1lbmNyeXB0ZWQta2V5"
        
        # Vérifier que subprocess.run a été appelé avec les bons arguments
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert "sudo" in call_args
        assert "-a" in call_args
        assert "-k" in call_args
        assert "-s" in call_args
        assert "-w" in call_args
        
        logger.info("✓ Chiffrement réussi")
    
    @patch.dict(os.environ, {"MAA_ENDPOINT": "https://test.attest.azure.net", 
                            "KEYVAULT_KEY": "https://test.vault.azure.net/keys/testkey/version",
                            "KEY_ENCRYPTED": "dGVzdC1lbmNyeXB0ZWQta2V5"})
    @patch('skr_client.platform.system')
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    @patch('os.access')
    def test_unwrap_key_success(self, mock_access, mock_exists, mock_subprocess, mock_platform):
        """Test déchiffrement réussi."""
        logger.info("=== Test déchiffrement réussi ===")
        
        # Setup mocks
        mock_platform.return_value = "Linux"
        mock_exists.return_value = True
        mock_access.return_value = True
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "test-secret-key"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        client = skr_client.SKRClient(debug=True)
        result = client.unwrap_key()
        
        assert result == "test-secret-key"
        
        # Vérifier que subprocess.run a été appelé avec les bons arguments
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert "sudo" in call_args
        assert "-u" in call_args
        
        logger.info("✓ Déchiffrement réussi")
    
    @patch.dict(os.environ, {"MAA_ENDPOINT": "https://test.attest.azure.net", 
                            "KEYVAULT_KEY": "https://test.vault.azure.net/keys/testkey/version"})
    @patch('skr_client.platform.system')
    def test_wrap_missing_key_fails(self, mock_platform):
        """Test échec chiffrement sans clé."""
        logger.info("=== Test échec chiffrement sans clé ===")
        
        mock_platform.return_value = "Linux"
        client = skr_client.SKRClient()
        
        with pytest.raises(ValueError, match="Variable d'environnement KEY manquante"):
            client.wrap_key()
        logger.info("✓ Erreur clé manquante correctement levée")
    
    @patch.dict(os.environ, {"MAA_ENDPOINT": "https://test.attest.azure.net", 
                            "KEYVAULT_KEY": "https://test.vault.azure.net/keys/testkey/version"})
    @patch('skr_client.platform.system')
    def test_unwrap_missing_encrypted_key_fails(self, mock_platform):
        """Test échec déchiffrement sans clé chiffrée."""
        logger.info("=== Test échec déchiffrement sans clé chiffrée ===")
        
        mock_platform.return_value = "Linux"
        client = skr_client.SKRClient()
        
        with pytest.raises(ValueError, match="Variable d'environnement KEY_ENCRYPTED manquante"):
            client.unwrap_key()
        logger.info("✓ Erreur clé chiffrée manquante correctement levée")
    
    @patch.dict(os.environ, {"MAA_ENDPOINT": "https://test.attest.azure.net", 
                            "KEYVAULT_KEY": "https://test.vault.azure.net/keys/testkey/version",
                            "KEY": "test-key"})
    @patch('skr_client.platform.system')
    @patch('pathlib.Path.exists')
    def test_executable_not_found_fails(self, mock_exists, mock_platform):
        """Test échec si exécutable introuvable."""
        logger.info("=== Test échec exécutable introuvable ===")
        
        mock_platform.return_value = "Linux"
        mock_exists.return_value = False
        
        client = skr_client.SKRClient()
        
        with pytest.raises(FileNotFoundError, match="Exécutable introuvable"):
            client.wrap_key()
        logger.info("✓ Erreur exécutable introuvable correctement levée")
    
    @patch.dict(os.environ, {"MAA_ENDPOINT": "https://test.attest.azure.net", 
                            "KEYVAULT_KEY": "https://test.vault.azure.net/keys/testkey/version",
                            "KEY": "test-key"})
    @patch('skr_client.platform.system')
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    @patch('os.access')
    def test_subprocess_error_handling(self, mock_access, mock_exists, mock_subprocess, mock_platform):
        """Test gestion d'erreur subprocess."""
        logger.info("=== Test gestion erreur subprocess ===")
        
        mock_platform.return_value = "Linux"
        mock_exists.return_value = True
        mock_access.return_value = True
        
        # Simuler une erreur subprocess
        mock_subprocess.side_effect = subprocess.CalledProcessError(
            1, ["sudo", "AzureAttestSKR"], output="", stderr="Erreur test"
        )
        
        client = skr_client.SKRClient(debug=True)
        
        with pytest.raises(subprocess.CalledProcessError):
            client.wrap_key()
        logger.info("✓ Erreur subprocess correctement propagée")


class TestMainFunction:
    """Tests pour la fonction main."""
    
    @patch('sys.argv', ['skr_client.py'])
    def test_main_no_args(self, capsys):
        """Test main sans arguments."""
        logger.info("=== Test main sans arguments ===")
        
        with pytest.raises(SystemExit):
            skr_client.main()
        
        captured = capsys.readouterr()
        assert "Usage:" in captured.out
        logger.info("✓ Usage affiché correctement")
    
    @patch('sys.argv', ['skr_client.py', 'invalid'])
    def test_main_invalid_operation(self, capsys):
        """Test main avec opération invalide."""
        logger.info("=== Test main opération invalide ===")
        
        with pytest.raises(SystemExit):
            skr_client.main()
        
        captured = capsys.readouterr()
        assert "Usage:" in captured.out
        logger.info("✓ Erreur opération invalide gérée")


@pytest.mark.integration
@pytest.mark.skipif(
    not (
        os.environ.get("RUN_INTEGRATION") and 
        platform.system() == "Linux" and
        os.environ.get("MAA_ENDPOINT") and
        os.environ.get("KEYVAULT_KEY") and
        (os.environ.get("KEY") or os.environ.get("KEY_ENCRYPTED"))
    ),
    reason="Test d'intégration skippé - variables d'environnement manquantes ou système non-Linux"
)
def test_integration_real_execution():
    """Test d'intégration avec exécution réelle."""
    logger.info("=== Test d'intégration réel ===")
    
    # Ce test nécessite un environnement configuré avec:
    # - RUN_INTEGRATION=1
    # - MAA_ENDPOINT, KEYVAULT_KEY, KEY ou KEY_ENCRYPTED
    # - Le binaire AzureAttestSKR dans le répertoire du projet
    
    client = skr_client.SKRClient(debug=True)
    
    if os.environ.get("KEY"):
        logger.info("Test chiffrement réel")
        result = client.wrap_key()
        assert result
        logger.info(f"Résultat chiffrement: {result[:20]}...")
    
    if os.environ.get("KEY_ENCRYPTED"):
        logger.info("Test déchiffrement réel")
        result = client.unwrap_key()
        assert result
        logger.info(f"Résultat déchiffrement: {result[:20]}...")
    
    logger.info("✓ Test d'intégration réussi")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])