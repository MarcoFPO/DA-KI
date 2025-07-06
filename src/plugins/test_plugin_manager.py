"""
Test-Skript für den erweiterten Plugin Manager.
Testet das Laden, Konfigurieren und Verwenden aller Datenquellen-Plugins.
"""
import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any

from .plugin_manager import PluginManager

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class PluginManagerTester:
    """Tester für den Plugin Manager."""
    
    def __init__(self):
        self.plugin_manager = PluginManager()
        
        # Beispiel-Konfigurationen für alle Plugins
        # HINWEIS: Diese enthalten Platzhalter-API-Keys - ersetzen Sie mit echten Keys
        self.test_configs = {
            "AlphaVantagePlugin": {
                "api_key": "YOUR_ALPHA_VANTAGE_API_KEY",
                "rate_limit_delay": 0.2,
                "premium_account": False
            },
            "YahooFinancePlugin": {
                "rate_limit_delay": 0.1,
                "enable_news": True,
                "enable_options": False
            },
            "FREDPlugin": {
                "api_key": "YOUR_FRED_API_KEY",
                "rate_limit_delay": 0.5,
                "default_frequency": "d"
            },
            "FinancialModelingPrepPlugin": {
                "api_key": "YOUR_FMP_API_KEY",
                "rate_limit_delay": 0.2,
                "enable_premium_features": False
            },
            "RedditSentimentPlugin": {
                "client_id": "YOUR_REDDIT_CLIENT_ID",
                "client_secret": "YOUR_REDDIT_CLIENT_SECRET",
                "user_agent": "DA-KI:v1.0 (by /u/your_username)",
                "rate_limit_delay": 1.0,
                "target_subreddits": ["stocks", "investing", "SecurityAnalysis"]
            },
            "NewsSentimentPlugin": {
                "newsapi_key": "YOUR_NEWSAPI_KEY",
                "finnhub_key": "YOUR_FINNHUB_KEY",
                "marketaux_key": "YOUR_MARKETAUX_KEY",
                "rate_limit_delay": 0.5
            }
        }
    
    async def test_plugin_loading(self):
        """Testet das Laden aller Plugins."""
        logger.info("🔧 Teste Plugin-Laden...")
        
        try:
            await self.plugin_manager.load_plugins()
            available_plugins = self.plugin_manager.get_available_plugins()
            
            logger.info(f"✅ {len(available_plugins)} Plugins geladen: {available_plugins}")
            
            # Zeige Konfigurationsschemas
            for plugin_name in available_plugins:
                schema = self.plugin_manager.get_plugin_config_schema(plugin_name)
                logger.info(f"📋 {plugin_name} Konfigurationsschema: {len(schema)} Parameter")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Plugins: {e}")
            return False
    
    async def test_plugin_status(self):
        """Testet die Status-Abfrage."""
        logger.info("📊 Teste Plugin-Status...")
        
        try:
            status = self.plugin_manager.get_status()
            logger.info(f"📊 Plugin Manager Status: {status['status']}")
            logger.info(f"📊 Plugins gesamt: {status['details']['total_plugins']}")
            logger.info(f"📊 Aktive Plugins: {status['details']['active_plugins']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Status-Check: {e}")
            return False
    
    async def test_yahoo_finance_plugin(self):
        """Testet das Yahoo Finance Plugin (benötigt keine API-Keys)."""
        logger.info("🧪 Teste Yahoo Finance Plugin...")
        
        try:
            # Konfiguriere Yahoo Finance Plugin
            config_result = await self.plugin_manager.configure_plugin(
                "YahooFinancePlugin", 
                self.test_configs["YahooFinancePlugin"]
            )
            
            if not config_result:
                logger.warning("⚠️ Yahoo Finance Plugin konnte nicht konfiguriert werden")
                return False
            
            # Teste OHLCV Daten
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            data = await self.plugin_manager.fetch_data_from_plugin(
                "YahooFinancePlugin",
                "ohlcv",
                "AAPL",
                start_date,
                end_date,
                interval="daily"
            )
            
            if data:
                logger.info(f"✅ Yahoo Finance: {len(data)} OHLCV-Datensätze für AAPL erhalten")
                logger.info(f"📈 Beispiel-Datensatz: {data[0] if data else 'Keine Daten'}")
                
                # Teste News-Daten
                news_data = await self.plugin_manager.fetch_data_from_plugin(
                    "YahooFinancePlugin",
                    "events",
                    "AAPL",
                    start_date,
                    end_date,
                    event_type="news"
                )
                
                logger.info(f"📰 Yahoo Finance: {len(news_data)} News-Artikel für AAPL erhalten")
                return True
            else:
                logger.warning("⚠️ Keine Daten von Yahoo Finance erhalten")
                return False
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Testen des Yahoo Finance Plugins: {e}")
            return False
    
    async def test_parallel_data_fetching(self):
        """Testet paralleles Daten-Abrufen von mehreren Plugins."""
        logger.info("⚡ Teste paralleles Daten-Abrufen...")
        
        try:
            # Aktiviere Yahoo Finance Plugin für Test
            await self.plugin_manager.configure_plugin(
                "YahooFinancePlugin", 
                self.test_configs["YahooFinancePlugin"]
            )
            
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            # Hole Daten von allen aktiven Plugins
            all_data = await self.plugin_manager.fetch_data_from_all_active_plugins(
                "ohlcv",
                "MSFT",
                start_date,
                end_date,
                interval="daily"
            )
            
            logger.info(f"⚡ Daten von {len(all_data)} aktiven Plugins erhalten:")
            for plugin_name, data in all_data.items():
                logger.info(f"  📊 {plugin_name}: {len(data)} Datensätze")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler beim parallelen Daten-Abrufen: {e}")
            return False
    
    async def test_plugin_configuration_schemas(self):
        """Testet die Konfigurationsschemas aller Plugins."""
        logger.info("🔧 Teste Plugin-Konfigurationsschemas...")
        
        try:
            for plugin_name in self.plugin_manager.get_available_plugins():
                schema = self.plugin_manager.get_plugin_config_schema(plugin_name)
                
                logger.info(f"📋 {plugin_name} Konfiguration:")
                for param_name, param_info in schema.items():
                    required = "✅" if param_info.get("required", False) else "⭕"
                    sensitive = "🔒" if param_info.get("sensitive", False) else "🔓"
                    logger.info(f"  {required} {sensitive} {param_name}: {param_info.get('description', '')}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Testen der Konfigurationsschemas: {e}")
            return False
    
    async def test_plugin_activation_deactivation(self):
        """Testet Aktivierung und Deaktivierung von Plugins."""
        logger.info("🔄 Teste Plugin-Aktivierung und -Deaktivierung...")
        
        try:
            # Aktiviere Yahoo Finance Plugin
            config_result = await self.plugin_manager.configure_plugin(
                "YahooFinancePlugin", 
                self.test_configs["YahooFinancePlugin"]
            )
            
            if config_result:
                logger.info("✅ Yahoo Finance Plugin aktiviert")
                
                # Status prüfen
                status = self.plugin_manager.get_status()
                active_plugins = status['details']['active_plugins']
                logger.info(f"📊 Aktive Plugins: {active_plugins}")
                
                # Deaktiviere Plugin
                deactivate_result = await self.plugin_manager.deactivate_plugin("YahooFinancePlugin")
                if deactivate_result:
                    logger.info("✅ Yahoo Finance Plugin deaktiviert")
                    
                    # Status erneut prüfen
                    status = self.plugin_manager.get_status()
                    active_plugins = status['details']['active_plugins']
                    logger.info(f"📊 Aktive Plugins nach Deaktivierung: {active_plugins}")
                
                return True
            else:
                logger.warning("⚠️ Plugin konnte nicht aktiviert werden")
                return False
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Testen der Plugin-Aktivierung: {e}")
            return False
    
    async def test_error_handling(self):
        """Testet Fehlerbehandlung."""
        logger.info("🚨 Teste Fehlerbehandlung...")
        
        try:
            # Teste nicht existierendes Plugin
            result = await self.plugin_manager.activate_plugin("NonExistentPlugin")
            if not result:
                logger.info("✅ Fehlerbehandlung für nicht existierendes Plugin funktioniert")
            
            # Teste Daten-Abruf von inaktivem Plugin
            data = await self.plugin_manager.fetch_data_from_plugin(
                "AlphaVantagePlugin",  # Nicht konfiguriert
                "ohlcv",
                "AAPL",
                "2024-01-01",
                "2024-01-31"
            )
            
            if not data:
                logger.info("✅ Fehlerbehandlung für inaktives Plugin funktioniert")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Testen der Fehlerbehandlung: {e}")
            return False
    
    async def run_all_tests(self):
        """Führt alle Tests aus."""
        logger.info("🚀 Starte Plugin Manager Tests...")
        
        tests = [
            ("Plugin-Laden", self.test_plugin_loading),
            ("Plugin-Status", self.test_plugin_status),
            ("Yahoo Finance Plugin", self.test_yahoo_finance_plugin),
            ("Konfigurationsschemas", self.test_plugin_configuration_schemas),
            ("Plugin-Aktivierung/Deaktivierung", self.test_plugin_activation_deactivation),
            ("Paralleles Daten-Abrufen", self.test_parallel_data_fetching),
            ("Fehlerbehandlung", self.test_error_handling)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*50}")
            logger.info(f"🧪 Test: {test_name}")
            logger.info(f"{'='*50}")
            
            try:
                result = await test_func()
                results.append((test_name, result))
                
                if result:
                    logger.info(f"✅ Test '{test_name}' erfolgreich")
                else:
                    logger.warning(f"⚠️ Test '{test_name}' fehlgeschlagen")
                    
            except Exception as e:
                logger.error(f"❌ Test '{test_name}' mit Fehler: {e}")
                results.append((test_name, False))
        
        # Zusammenfassung
        logger.info(f"\n{'='*50}")
        logger.info("📊 TEST-ZUSAMMENFASSUNG")
        logger.info(f"{'='*50}")
        
        successful_tests = sum(1 for _, result in results if result)
        total_tests = len(results)
        
        for test_name, result in results:
            status = "✅ ERFOLGREICH" if result else "❌ FEHLGESCHLAGEN"
            logger.info(f"{status} - {test_name}")
        
        logger.info(f"\n🎯 {successful_tests}/{total_tests} Tests erfolgreich")
        
        if successful_tests == total_tests:
            logger.info("🎉 Alle Tests erfolgreich! Plugin Manager ist einsatzbereit.")
        else:
            logger.warning("⚠️ Einige Tests fehlgeschlagen. Überprüfen Sie die Konfiguration.")
        
        # Cleanup
        await self.plugin_manager.close_plugins()
        logger.info("🔧 Plugin Manager geschlossen.")


async def main():
    """Hauptfunktion zum Ausführen der Tests."""
    tester = PluginManagerTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())