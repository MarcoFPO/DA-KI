import importlib
import inspect
import os
import sys
from typing import Dict, Any, List, Type, Optional
import logging
import asyncio
from datetime import datetime

from src.plugins.data_sources.data_source_plugin import DataSourcePlugin

# Import all available data source plugins
from src.plugins.data_sources.alpha_vantage_plugin import AlphaVantagePlugin
from src.plugins.data_sources.yahoo_finance_plugin import YahooFinancePlugin
from src.plugins.data_sources.fred_plugin import FREDPlugin
from src.plugins.data_sources.financial_modeling_prep_plugin import FinancialModelingPrepPlugin
from src.plugins.data_sources.reddit_sentiment_plugin import RedditSentimentPlugin
from src.plugins.data_sources.news_sentiment_plugin import NewsSentimentPlugin

logger = logging.getLogger(__name__)

class PluginManager:
    """
    Verwaltet das Laden, Aktivieren, Deaktivieren und Neuladen von Plugins.
    Unterstützt alle implementierten Datenquellen-Plugins:
    - Alpha Vantage: Umfassende Finanzmarktdaten
    - Yahoo Finance: Kostenlose Marktdaten und News
    - FRED: Makroökonomische Daten der Federal Reserve
    - Financial Modeling Prep: Premium Finanzanalyse-Daten
    - Reddit Sentiment: Social Media Sentiment-Analyse
    - News Sentiment: Nachrichten-Sentiment-Analyse
    """
    _instance = None
    _is_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PluginManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._is_initialized:
            self.plugins: Dict[str, DataSourcePlugin] = {}
            self.plugin_configs: Dict[str, Dict[str, Any]] = {}
            self.plugin_base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), './data_sources')
            self.active_plugins: Dict[str, bool] = {}
            self.plugin_classes = {
                "AlphaVantagePlugin": AlphaVantagePlugin,
                "YahooFinancePlugin": YahooFinancePlugin,
                "FREDPlugin": FREDPlugin,
                "FinancialModelingPrepPlugin": FinancialModelingPrepPlugin,
                "RedditSentimentPlugin": RedditSentimentPlugin,
                "NewsSentimentPlugin": NewsSentimentPlugin
            }
            self._is_initialized = True

    async def load_plugins(self):
        """
        Lädt alle verfügbaren Datenquellen-Plugins.
        """
        logger.info(f"Loading data source plugins...")
        
        for plugin_class_name, plugin_class in self.plugin_classes.items():
            try:
                # Instanziiere das Plugin
                plugin_instance = plugin_class()
                plugin_name = plugin_instance.get_name()
                
                self.plugins[plugin_name] = plugin_instance
                self.active_plugins[plugin_name] = False  # Standardmäßig inaktiv
                
                logger.info(f"Plugin '{plugin_name}' ({plugin_class_name}) erfolgreich geladen.")
                
            except Exception as e:
                logger.error(f"Fehler beim Laden des Plugins '{plugin_class_name}': {e}")
        
        logger.info(f"Insgesamt {len(self.plugins)} Plugins geladen: {list(self.plugins.keys())}")

    async def initialize_plugins(self, plugin_configs: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Initialisiert alle geladenen Plugins mit ihren Konfigurationen.
        
        Args:
            plugin_configs: Konfigurationen für die Plugins. Falls None, werden Default-Konfigurationen verwendet.
        """
        if plugin_configs:
            self.plugin_configs.update(plugin_configs)
        
        for plugin_name, plugin_instance in self.plugins.items():
            config = self.plugin_configs.get(plugin_name, {})
            try:
                if config:  # Nur initialisieren wenn Konfiguration vorhanden
                    plugin_instance.initialize(config)
                    self.active_plugins[plugin_name] = True
                    logger.info(f"Plugin '{plugin_name}' initialisiert und aktiviert.")
                else:
                    logger.info(f"Plugin '{plugin_name}' geladen aber nicht konfiguriert - verwende get_config_schema() für Setup.")
            except Exception as e:
                logger.error(f"Fehler beim Initialisieren von Plugin '{plugin_name}': {e}")
                self.active_plugins[plugin_name] = False

    async def reload_plugins(self):
        """
        Lädt alle Plugins neu und initialisiert sie erneut.
        """
        logger.info("Plugins werden neu geladen...")
        await self.close_plugins()
        self.plugins.clear()
        self._is_initialized = False # Reset für __init__ Singleton
        self.__init__()
        await self.load_plugins()
        await self.initialize_plugins()
        logger.info("Plugins erfolgreich neu geladen.")

    async def close_plugins(self):
        """
        Führt die Bereinigungsarbeiten für alle geladenen Plugins durch.
        """
        for plugin_name, plugin_instance in self.plugins.items():
            try:
                await plugin_instance.close()
                logger.info(f"Plugin '{plugin_name}' geschlossen.")
            except Exception as e:
                logger.error(f"Fehler beim Schließen von Plugin '{plugin_name}': {e}")

    def get_plugin(self, name: str) -> Optional[DataSourcePlugin]:
        """
        Gibt eine Plugin-Instanz nach Namen zurück.
        
        Args:
            name: Name des Plugins
            
        Returns:
            Plugin-Instanz oder None falls nicht gefunden
        """
        return self.plugins.get(name)
    
    def get_active_plugins(self) -> Dict[str, DataSourcePlugin]:
        """
        Gibt alle aktiven Plugins zurück.
        
        Returns:
            Dictionary mit aktiven Plugin-Instanzen
        """
        return {name: plugin for name, plugin in self.plugins.items() 
                if self.active_plugins.get(name, False)}
    
    def get_available_plugins(self) -> List[str]:
        """
        Gibt eine Liste aller verfügbaren Plugin-Namen zurück.
        
        Returns:
            Liste der Plugin-Namen
        """
        return list(self.plugins.keys())
    
    def get_plugin_config_schema(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """
        Gibt das Konfigurationsschema für ein Plugin zurück.
        
        Args:
            plugin_name: Name des Plugins
            
        Returns:
            Konfigurationsschema oder None falls Plugin nicht gefunden
        """
        plugin = self.get_plugin(plugin_name)
        if plugin:
            return plugin.get_config_schema()
        return None

    def get_status(self) -> Dict[str, Any]:
        """
        Gibt den Status des PluginManagers und aller geladenen Plugins zurück.
        """
        active_count = sum(1 for active in self.active_plugins.values() if active)
        inactive_count = len(self.plugins) - active_count
        
        status = {
            "status": "OK",
            "message": "PluginManager operational",
            "timestamp": datetime.now().isoformat(),
            "details": {
                "total_plugins": len(self.plugins),
                "active_plugins": active_count,
                "inactive_plugins": inactive_count,
                "failed_plugins_count": 0,
                "plugins": {}
            }
        }
        
        for plugin_name, plugin_instance in self.plugins.items():
            try:
                plugin_status = plugin_instance.get_status()
                plugin_status["active"] = self.active_plugins.get(plugin_name, False)
                plugin_status["configured"] = plugin_name in self.plugin_configs
                status["details"]["plugins"][plugin_name] = plugin_status
                
                # Check for plugin errors
                if plugin_status.get("status") == "ERROR" or plugin_status.get("status") == "inactive":
                    if self.active_plugins.get(plugin_name, False):  # Nur zählen wenn Plugin aktiv sein sollte
                        status["details"]["failed_plugins_count"] += 1
                        if status["status"] == "OK":
                            status["status"] = "WARNING"
                            status["message"] = "Ein oder mehrere aktive Plugins haben Probleme."
                            
            except Exception as e:
                logger.error(f"Fehler beim Abrufen des Status von Plugin '{plugin_name}': {e}")
                status["details"]["plugins"][plugin_name] = {
                    "status": "ERROR", 
                    "message": f"Status check failed: {e}",
                    "active": self.active_plugins.get(plugin_name, False),
                    "configured": plugin_name in self.plugin_configs
                }
                status["details"]["failed_plugins_count"] += 1
                status["status"] = "ERROR"
                status["message"] = "Ein oder mehrere Plugins haben Fehler."
        
        return status

    async def configure_plugin(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """
        Konfiguriert und aktiviert ein Plugin.
        
        Args:
            plugin_name: Name des zu konfigurierenden Plugins
            config: Konfigurationsdaten für das Plugin
            
        Returns:
            True wenn erfolgreich konfiguriert, False sonst
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            logger.warning(f"Plugin '{plugin_name}' nicht gefunden.")
            return False
        
        try:
            plugin.initialize(config)
            self.plugin_configs[plugin_name] = config
            self.active_plugins[plugin_name] = True
            logger.info(f"Plugin '{plugin_name}' erfolgreich konfiguriert und aktiviert.")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Konfigurieren von Plugin '{plugin_name}': {e}")
            self.active_plugins[plugin_name] = False
            return False
    
    async def activate_plugin(self, plugin_name: str) -> bool:
        """
        Aktiviert ein bereits konfiguriertes Plugin.
        
        Args:
            plugin_name: Name des zu aktivierenden Plugins
            
        Returns:
            True wenn erfolgreich aktiviert, False sonst
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            logger.warning(f"Plugin '{plugin_name}' nicht gefunden.")
            return False
        
        if plugin_name not in self.plugin_configs:
            logger.warning(f"Plugin '{plugin_name}' ist nicht konfiguriert. Verwende configure_plugin() zuerst.")
            return False
        
        try:
            # Re-initialize with existing config if needed
            config = self.plugin_configs[plugin_name]
            plugin.initialize(config)
            self.active_plugins[plugin_name] = True
            logger.info(f"Plugin '{plugin_name}' aktiviert.")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Aktivieren von Plugin '{plugin_name}': {e}")
            return False

    async def deactivate_plugin(self, plugin_name: str) -> bool:
        """
        Deaktiviert ein Plugin.
        
        Args:
            plugin_name: Name des zu deaktivierenden Plugins
            
        Returns:
            True wenn erfolgreich deaktiviert, False sonst
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            logger.warning(f"Plugin '{plugin_name}' nicht gefunden.")
            return False
        
        try:
            await plugin.close()
            self.active_plugins[plugin_name] = False
            logger.info(f"Plugin '{plugin_name}' deaktiviert.")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Deaktivieren von Plugin '{plugin_name}': {e}")
            return False
    
    async def fetch_data_from_plugin(self, plugin_name: str, data_type: str, ticker: str, 
                                   start_date: str, end_date: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Holt Daten von einem spezifischen Plugin.
        
        Args:
            plugin_name: Name des Plugins
            data_type: Typ der Daten ('ohlcv', 'indicators', 'events')
            ticker: Ticker-Symbol
            start_date: Startdatum (YYYY-MM-DD)
            end_date: Enddatum (YYYY-MM-DD)
            **kwargs: Zusätzliche Parameter
            
        Returns:
            Liste von Datensätzen oder leere Liste bei Fehlern
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            logger.warning(f"Plugin '{plugin_name}' nicht gefunden.")
            return []
        
        if not self.active_plugins.get(plugin_name, False):
            logger.warning(f"Plugin '{plugin_name}' ist nicht aktiv.")
            return []
        
        try:
            if data_type.lower() == 'ohlcv':
                interval = kwargs.get('interval', 'daily')
                return await plugin.fetch_ohlcv_data(ticker, start_date, end_date, interval)
            
            elif data_type.lower() == 'indicators':
                indicator_type = kwargs.get('indicator_type', '')
                params = kwargs.get('params', {})
                return await plugin.fetch_technical_indicators(ticker, indicator_type, params)
            
            elif data_type.lower() == 'events':
                event_type = kwargs.get('event_type', '')
                return await plugin.fetch_event_data(ticker, event_type, start_date, end_date)
            
            else:
                logger.warning(f"Unbekannter Datentyp: {data_type}")
                return []
                
        except Exception as e:
            logger.error(f"Fehler beim Abrufen von Daten von Plugin '{plugin_name}': {e}")
            return []
    
    async def fetch_data_from_all_active_plugins(self, data_type: str, ticker: str, 
                                               start_date: str, end_date: str, **kwargs) -> Dict[str, List[Dict[str, Any]]]:
        """
        Holt Daten von allen aktiven Plugins.
        
        Args:
            data_type: Typ der Daten ('ohlcv', 'indicators', 'events')
            ticker: Ticker-Symbol
            start_date: Startdatum (YYYY-MM-DD)
            end_date: Enddatum (YYYY-MM-DD)
            **kwargs: Zusätzliche Parameter
            
        Returns:
            Dictionary mit Plugin-Namen als Keys und Datenlisten als Values
        """
        results = {}
        
        # Erstelle Tasks für alle aktiven Plugins
        tasks = []
        active_plugin_names = []
        
        for plugin_name, is_active in self.active_plugins.items():
            if is_active:
                task = self.fetch_data_from_plugin(plugin_name, data_type, ticker, start_date, end_date, **kwargs)
                tasks.append(task)
                active_plugin_names.append(plugin_name)
        
        if not tasks:
            logger.warning("Keine aktiven Plugins gefunden.")
            return results
        
        # Führe alle Tasks parallel aus
        try:
            data_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(data_results):
                plugin_name = active_plugin_names[i]
                if isinstance(result, Exception):
                    logger.error(f"Fehler beim Abrufen von Daten von Plugin '{plugin_name}': {result}")
                    results[plugin_name] = []
                else:
                    results[plugin_name] = result
                    
        except Exception as e:
            logger.error(f"Fehler beim parallelen Abrufen von Daten: {e}")
        
        return results
