"""
Improved configuration management with better security practices.
"""
import os
import json
import base64
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Configuration-related errors."""
    pass


class SecureConfig:
    """Secure configuration management class."""
    
    _secrets: Dict[str, Any] = {}
    _is_loaded: bool = False
    _environment: str = "development"
    
    @classmethod
    def load_secrets(cls) -> None:
        """Load configuration based on environment."""
        if cls._is_loaded:
            return
        
        cls._environment = os.getenv("DAKI_ENV", "development")
        
        if cls._environment == "development":
            cls._load_development_config()
        elif cls._environment == "production":
            cls._load_production_config()
        else:
            logger.warning(f"Unknown environment: {cls._environment}. Using minimal config.")
            cls._secrets = cls._get_minimal_config()
        
        cls._is_loaded = True
        logger.info(f"Configuration loaded for environment: {cls._environment}")
    
    @classmethod
    def _load_development_config(cls) -> None:
        """Load development configuration from file."""
        secrets_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            '../../config/dev_secrets.json'
        )
        
        try:
            with open(secrets_file, 'r') as f:
                cls._secrets = json.load(f)
            logger.info(f"Development secrets loaded from {secrets_file}")
            
            # Validate required fields
            cls._validate_development_config()
            
        except FileNotFoundError:
            logger.warning(f"Development secrets file not found: {secrets_file}")
            cls._secrets = cls._get_minimal_config()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in secrets file: {e}")
            raise ConfigError(f"Invalid configuration file: {e}")
        except Exception as e:
            logger.error(f"Error loading development config: {e}")
            raise ConfigError(f"Configuration error: {e}")
    
    @classmethod
    def _load_production_config(cls) -> None:
        """Load production configuration from environment variables."""
        try:
            prod_secrets = {}
            
            # Load critical environment variables
            required_env_vars = [
                "DAKI_SECRET_KEY",
                "DAKI_DATABASE_URL",
                "DAKI_MASTER_ENCRYPTION_KEY"
            ]
            
            missing_vars = []
            for var in required_env_vars:
                value = os.getenv(var)
                if not value:
                    missing_vars.append(var)
                else:
                    # Convert environment variable names to config structure
                    config_key = var.replace("DAKI_", "").lower()
                    if config_key == "secret_key":
                        prod_secrets.setdefault("jwt", {})["secret_key"] = value
                    elif config_key == "database_url":
                        prod_secrets.setdefault("database", {})["url"] = value
                    elif config_key == "master_encryption_key":
                        try:
                            decoded_key = base64.b64decode(value)
                            prod_secrets.setdefault("system", {})["master_encryption_key"] = decoded_key
                        except Exception as e:
                            logger.error(f"Error decoding master encryption key: {e}")
                            missing_vars.append(var)
            
            if missing_vars:
                raise ConfigError(f"Missing required environment variables: {missing_vars}")
            
            # Load optional API keys
            optional_vars = {
                "DAKI_ALPHA_VANTAGE_KEY": ["api_keys", "alpha_vantage"],
                "DAKI_YAHOO_FINANCE_KEY": ["api_keys", "yahoo_finance"],
                "DAKI_BROKER_API_KEY": ["api_keys", "broker", "key"],
                "DAKI_BROKER_API_SECRET": ["api_keys", "broker", "secret"],
            }
            
            for env_var, config_path in optional_vars.items():
                value = os.getenv(env_var)
                if value:
                    current_level = prod_secrets
                    for i, key in enumerate(config_path):
                        if i == len(config_path) - 1:
                            current_level[key] = value
                        else:
                            current_level = current_level.setdefault(key, {})
            
            cls._secrets = prod_secrets
            logger.info("Production configuration loaded from environment variables")
            
        except ConfigError:
            raise
        except Exception as e:
            logger.error(f"Error loading production config: {e}")
            raise ConfigError(f"Production configuration error: {e}")
    
    @classmethod
    def _validate_development_config(cls) -> None:
        """Validate development configuration structure."""
        required_sections = ["database", "jwt"]
        
        for section in required_sections:
            if section not in cls._secrets:
                logger.warning(f"Missing required config section: {section}")
                cls._secrets[section] = {}
        
        # Ensure JWT secret is set
        if not cls._secrets.get("jwt", {}).get("secret_key"):
            cls._secrets.setdefault("jwt", {})["secret_key"] = cls._generate_dev_jwt_secret()
            logger.warning("Generated temporary JWT secret for development")
    
    @classmethod
    def _get_minimal_config(cls) -> Dict[str, Any]:
        """Get minimal configuration for fallback."""
        return {
            "database": {
                "url": "sqlite:///./data/daki.db"
            },
            "jwt": {
                "secret_key": cls._generate_dev_jwt_secret(),
                "access_token_expire_minutes": 30,
                "refresh_token_expire_days": 7
            },
            "api_keys": {},
            "users": {
                "admin": {
                    "username": "admin",
                    "password": "admin123"  # Only for minimal config
                }
            }
        }
    
    @classmethod
    def _generate_dev_jwt_secret(cls) -> str:
        """Generate a secure JWT secret for development."""
        import secrets
        return secrets.token_urlsafe(32)
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if not cls._is_loaded:
            cls.load_secrets()
        
        return cls._secrets.get(key, default)
    
    @classmethod
    def get_nested(cls, *keys: str, default: Any = None) -> Any:
        """
        Get nested configuration value.
        
        Args:
            *keys: Nested configuration keys
            default: Default value if key not found
            
        Returns:
            Configuration value or default
            
        Example:
            get_nested("jwt", "secret_key") -> cls._secrets["jwt"]["secret_key"]
        """
        if not cls._is_loaded:
            cls.load_secrets()
        
        current = cls._secrets
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    @classmethod
    def get_jwt_secret(cls) -> str:
        """
        Get JWT secret key with validation.
        
        Returns:
            JWT secret key
            
        Raises:
            ConfigError: If JWT secret is not configured
        """
        secret = cls.get_nested("jwt", "secret_key")
        if not secret:
            raise ConfigError("JWT secret key not configured")
        
        if len(secret) < 32:
            logger.warning("JWT secret key is shorter than recommended (32 characters)")
        
        return secret
    
    @classmethod
    def get_database_url(cls) -> str:
        """
        Get database URL.
        
        Returns:
            Database URL
        """
        return cls.get_nested("database", "url", "sqlite:///./data/daki.db")
    
    @classmethod
    def get_api_key(cls, service: str) -> Optional[str]:
        """
        Get API key for a service.
        
        Args:
            service: Service name (e.g., 'alpha_vantage', 'yahoo_finance')
            
        Returns:
            API key or None if not configured
        """
        return cls.get_nested("api_keys", service)
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode."""
        if not cls._is_loaded:
            cls.load_secrets()
        return cls._environment == "development"
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode."""
        if not cls._is_loaded:
            cls.load_secrets()
        return cls._environment == "production"
    
    @classmethod
    def get_environment(cls) -> str:
        """Get current environment."""
        if not cls._is_loaded:
            cls.load_secrets()
        return cls._environment
    
    @classmethod
    def get_config_summary(cls) -> Dict[str, Any]:
        """
        Get configuration summary for debugging (without secrets).
        
        Returns:
            Configuration summary
        """
        if not cls._is_loaded:
            cls.load_secrets()
        
        summary = {
            "environment": cls._environment,
            "database_configured": bool(cls.get_nested("database", "url")),
            "jwt_configured": bool(cls.get_nested("jwt", "secret_key")),
            "api_keys_configured": list(cls.get("api_keys", {}).keys()),
            "config_sections": list(cls._secrets.keys())
        }
        
        return summary


# Create singleton instance for backward compatibility
Config = SecureConfig