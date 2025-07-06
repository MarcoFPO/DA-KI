"""
Plugin Manager Demo - Zeigt die Funktionalität ohne externe Abhängigkeiten.
"""
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class MockDataSourcePlugin:
    """Mock-Plugin für Demonstrationszwecke."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.initialized = False
        self.config = {}
    
    def get_name(self) -> str:
        return self.name
    
    def get_description(self) -> str:
        return self.description
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "api_key": {
                "type": "string",
                "description": f"API key for {self.name}",
                "required": True,
                "sensitive": True
            },
            "rate_limit_delay": {
                "type": "number",
                "description": "Delay between API calls",
                "default": 1.0,
                "min": 0.1,
                "max": 10.0
            }
        }
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        if not config.get("api_key"):
            raise ValueError(f"{self.name} requires an API key")
        
        self.config = config
        self.initialized = True
        logger.info(f"✅ {self.name} initialized with config: {list(config.keys())}")
    
    async def close(self) -> None:
        """Close plugin."""
        self.initialized = False
        logger.info(f"🔒 {self.name} closed")
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status."""
        return {
            "name": self.name,
            "status": "active" if self.initialized else "inactive",
            "description": self.description,
            "api_key_configured": bool(self.config.get("api_key")),
            "config_params": len(self.config)
        }
    
    async def fetch_ohlcv_data(self, ticker: str, start_date: str, end_date: str, interval: str = "daily") -> List[Dict[str, Any]]:
        """Mock OHLCV data fetching."""
        if not self.initialized:
            return []
        
        # Simuliere Daten
        mock_data = [
            {
                "date": "2024-01-01",
                "open": 150.0,
                "high": 155.0,
                "low": 148.0,
                "close": 152.0,
                "volume": 1000000,
                "source": self.name.lower().replace("plugin", ""),
                "ticker": ticker
            }
        ]
        
        logger.info(f"📊 {self.name}: Generated {len(mock_data)} mock OHLCV records for {ticker}")
        return mock_data


class PluginManagerDemo:
    """Vereinfachte Plugin Manager Demo."""
    
    def __init__(self):
        self.plugins: Dict[str, MockDataSourcePlugin] = {}
        self.active_plugins: Dict[str, bool] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        
        # Erstelle Mock-Plugins
        self.mock_plugins = {
            "AlphaVantagePlugin": MockDataSourcePlugin(
                "AlphaVantagePlugin", 
                "Premium financial data provider"
            ),
            "YahooFinancePlugin": MockDataSourcePlugin(
                "YahooFinancePlugin", 
                "Free financial data provider"
            ),
            "FREDPlugin": MockDataSourcePlugin(
                "FREDPlugin", 
                "Federal Reserve economic data"
            ),
            "FinancialModelingPrepPlugin": MockDataSourcePlugin(
                "FinancialModelingPrepPlugin", 
                "Comprehensive financial analysis"
            ),
            "RedditSentimentPlugin": MockDataSourcePlugin(
                "RedditSentimentPlugin", 
                "Social media sentiment analysis"
            ),
            "NewsSentimentPlugin": MockDataSourcePlugin(
                "NewsSentimentPlugin", 
                "News sentiment analysis"
            )
        }
    
    async def load_plugins(self):
        """Load all mock plugins."""
        logger.info("🔧 Loading plugins...")
        
        for plugin_name, plugin_instance in self.mock_plugins.items():
            self.plugins[plugin_name] = plugin_instance
            self.active_plugins[plugin_name] = False
            logger.info(f"📦 Loaded: {plugin_name}")
        
        logger.info(f"✅ {len(self.plugins)} plugins loaded successfully")
    
    def get_available_plugins(self) -> List[str]:
        """Get list of available plugins."""
        return list(self.plugins.keys())
    
    def get_plugin_config_schema(self, plugin_name: str) -> Dict[str, Any]:
        """Get configuration schema for a plugin."""
        plugin = self.plugins.get(plugin_name)
        if plugin:
            return plugin.get_config_schema()
        return {}
    
    async def configure_plugin(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """Configure and activate a plugin."""
        plugin = self.plugins.get(plugin_name)
        if not plugin:
            logger.error(f"❌ Plugin {plugin_name} not found")
            return False
        
        try:
            plugin.initialize(config)
            self.plugin_configs[plugin_name] = config
            self.active_plugins[plugin_name] = True
            logger.info(f"✅ {plugin_name} configured and activated")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to configure {plugin_name}: {e}")
            return False
    
    async def deactivate_plugin(self, plugin_name: str) -> bool:
        """Deactivate a plugin."""
        plugin = self.plugins.get(plugin_name)
        if not plugin:
            return False
        
        await plugin.close()
        self.active_plugins[plugin_name] = False
        logger.info(f"🔒 {plugin_name} deactivated")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall status."""
        active_count = sum(1 for active in self.active_plugins.values() if active)
        
        status = {
            "status": "OK",
            "total_plugins": len(self.plugins),
            "active_plugins": active_count,
            "inactive_plugins": len(self.plugins) - active_count,
            "plugins": {}
        }
        
        for plugin_name, plugin in self.plugins.items():
            plugin_status = plugin.get_status()
            plugin_status["active"] = self.active_plugins.get(plugin_name, False)
            status["plugins"][plugin_name] = plugin_status
        
        return status
    
    async def fetch_data_from_all_active_plugins(self, ticker: str, start_date: str, end_date: str) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch data from all active plugins."""
        results = {}
        
        for plugin_name, is_active in self.active_plugins.items():
            if is_active:
                plugin = self.plugins[plugin_name]
                data = await plugin.fetch_ohlcv_data(ticker, start_date, end_date)
                results[plugin_name] = data
        
        return results
    
    async def close_all_plugins(self):
        """Close all plugins."""
        for plugin_name, plugin in self.plugins.items():
            if self.active_plugins.get(plugin_name, False):
                await plugin.close()
        logger.info("🔒 All plugins closed")


async def demo():
    """Demonstrate the Plugin Manager functionality."""
    print("🚀 DA-KI Plugin Manager Demo")
    print("=" * 50)
    
    # Initialize Plugin Manager
    pm = PluginManagerDemo()
    await pm.load_plugins()
    
    print(f"\n📋 Available Plugins:")
    for plugin_name in pm.get_available_plugins():
        print(f"  • {plugin_name}")
    
    # Show initial status
    print(f"\n📊 Initial Status:")
    status = pm.get_status()
    print(f"  Total: {status['total_plugins']}")
    print(f"  Active: {status['active_plugins']}")
    print(f"  Inactive: {status['inactive_plugins']}")
    
    # Show configuration schemas
    print(f"\n🔧 Configuration Schemas:")
    for plugin_name in pm.get_available_plugins()[:2]:  # Show first 2
        schema = pm.get_plugin_config_schema(plugin_name)
        print(f"\n  {plugin_name}:")
        for param, details in schema.items():
            required = "✅" if details.get("required") else "⭕"
            sensitive = "🔒" if details.get("sensitive") else "🔓"
            print(f"    {required} {sensitive} {param}: {details.get('description', '')}")
    
    # Configure some plugins
    print(f"\n⚙️ Configuring Plugins:")
    
    configs = {
        "YahooFinancePlugin": {
            "api_key": "demo_yahoo_key",
            "rate_limit_delay": 0.1
        },
        "FREDPlugin": {
            "api_key": "demo_fred_key", 
            "rate_limit_delay": 0.5
        }
    }
    
    for plugin_name, config in configs.items():
        success = await pm.configure_plugin(plugin_name, config)
        if success:
            print(f"  ✅ {plugin_name} configured")
        else:
            print(f"  ❌ {plugin_name} configuration failed")
    
    # Show updated status
    print(f"\n📊 Updated Status:")
    status = pm.get_status()
    print(f"  Active: {status['active_plugins']}")
    print(f"  Inactive: {status['inactive_plugins']}")
    
    # Test data fetching
    print(f"\n📈 Testing Data Fetching:")
    data_results = await pm.fetch_data_from_all_active_plugins("AAPL", "2024-01-01", "2024-01-31")
    
    for plugin_name, data in data_results.items():
        print(f"  📊 {plugin_name}: {len(data)} records")
        if data:
            sample = data[0]
            print(f"    Sample: {sample['ticker']} - Close: ${sample['close']}")
    
    # Test deactivation
    print(f"\n🔒 Testing Plugin Deactivation:")
    await pm.deactivate_plugin("YahooFinancePlugin")
    
    # Final status
    print(f"\n📊 Final Status:")
    status = pm.get_status()
    print(f"  Active: {status['active_plugins']}")
    
    # Cleanup
    await pm.close_all_plugins()
    
    print(f"\n🎉 Demo completed successfully!")
    print(f"\n💡 Next Steps:")
    print(f"  1. Install dependencies: pip install aiohttp pydantic")
    print(f"  2. Get API keys from data providers")
    print(f"  3. Configure plugins with real credentials")
    print(f"  4. Run full integration tests")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())