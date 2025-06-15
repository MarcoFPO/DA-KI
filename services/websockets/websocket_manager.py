#!/usr/bin/env python3
"""
🔄 WebSocket Real-time Updates Manager für DA-KI
High-Performance Real-time Data Broadcasting

Entwickelt mit Claude Code - Real-time Communication Architecture
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Set, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import weakref
import uuid
from contextlib import asynccontextmanager

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False
    WebSocketServerProtocol = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """WebSocket Message Types"""
    STOCK_UPDATE = "stock_update"
    PORTFOLIO_UPDATE = "portfolio_update"
    MARKET_STATUS = "market_status"
    SYSTEM_STATUS = "system_status"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"

class ConnectionStatus(Enum):
    """Connection Status"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"

@dataclass
class WebSocketMessage:
    """Standardisierte WebSocket Message"""
    type: MessageType
    data: Any
    timestamp: datetime = None
    client_id: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps({
            'type': self.type.value,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'client_id': self.client_id
        }, default=str)

@dataclass
class ClientConnection:
    """Client Connection Information"""
    id: str
    websocket: Any  # WebSocketServerProtocol
    subscriptions: Set[str]
    connected_at: datetime
    last_ping: datetime = None
    status: ConnectionStatus = ConnectionStatus.CONNECTED
    
    def __post_init__(self):
        if self.last_ping is None:
            self.last_ping = self.connected_at

class WebSocketManager:
    """
    High-Performance WebSocket Manager für Real-time Updates
    
    Features:
    - Connection Management mit Auto-Reconnect
    - Subscription-based Message Routing
    - Broadcast & Unicast Messaging
    - Health Monitoring mit Ping/Pong
    - Rate Limiting & Error Handling
    - Performance Analytics
    """
    
    def __init__(self, 
                 host: str = "10.1.1.110",
                 port: int = 8765,
                 ping_interval: int = 30,
                 max_connections: int = 1000):
        
        self.host = host
        self.port = port
        self.ping_interval = ping_interval
        self.max_connections = max_connections
        
        # Connection Management
        self.clients: Dict[str, ClientConnection] = {}
        self.subscriptions: Dict[str, Set[str]] = {}  # topic -> client_ids
        
        # Server State
        self.server = None
        self.is_running = False
        
        # Performance Metrics
        self.metrics = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'broadcasts': 0,
            'errors': 0,
            'uptime_start': None
        }
        
        # Message Queues
        self.broadcast_queue = asyncio.Queue()
        self.message_handlers: Dict[MessageType, Callable] = {}
        
        # Health Check
        self.last_health_check = datetime.now()
        self.health_check_interval = 60  # seconds
        
    async def start_server(self):
        """Start WebSocket Server"""
        if not HAS_WEBSOCKETS:
            logger.error("❌ WebSockets library not available")
            return False
            
        try:
            logger.info(f"🚀 Starting WebSocket server on {self.host}:{self.port}")
            
            self.server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port,
                ping_interval=self.ping_interval,
                ping_timeout=10,
                max_size=2**20,  # 1MB max message size
                max_queue=32
            )
            
            self.is_running = True
            self.metrics['uptime_start'] = datetime.now()
            
            # Start background tasks
            asyncio.create_task(self.broadcast_worker())
            asyncio.create_task(self.health_check_worker())
            
            logger.info(f"✅ WebSocket server started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start WebSocket server: {e}")
            return False
    
    async def stop_server(self):
        """Stop WebSocket Server"""
        if self.server:
            logger.info("🔴 Stopping WebSocket server...")
            
            # Disconnect all clients
            await self.disconnect_all_clients()
            
            # Stop server
            self.server.close()
            await self.server.wait_closed()
            
            self.is_running = False
            logger.info("✅ WebSocket server stopped")
    
    async def handle_client(self, websocket, path):
        """Handle individual client connection"""
        client_id = str(uuid.uuid4())
        client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
        
        logger.info(f"🔗 New client connection: {client_id} from {client_ip}")
        
        # Check connection limit
        if len(self.clients) >= self.max_connections:
            await websocket.close(code=1008, reason="Connection limit reached")
            logger.warning(f"❌ Connection limit reached, rejected {client_id}")
            return
        
        # Create client connection
        client = ClientConnection(
            id=client_id,
            websocket=websocket,
            subscriptions=set(),
            connected_at=datetime.now()
        )
        
        self.clients[client_id] = client
        self.metrics['total_connections'] += 1
        self.metrics['active_connections'] = len(self.clients)
        
        try:
            # Send welcome message
            welcome_msg = WebSocketMessage(
                type=MessageType.SYSTEM_STATUS,
                data={
                    "status": "connected",
                    "client_id": client_id,
                    "server_time": datetime.now().isoformat(),
                    "available_subscriptions": list(self.subscriptions.keys())
                },
                client_id=client_id
            )
            await self.send_to_client(client_id, welcome_msg)
            
            # Handle messages
            async for message in websocket:
                await self.handle_message(client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 Client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"❌ Error handling client {client_id}: {e}")
            self.metrics['errors'] += 1
        finally:
            await self.disconnect_client(client_id)
    
    async def handle_message(self, client_id: str, message: str):
        """Handle incoming message from client"""
        try:
            data = json.loads(message)
            message_type = MessageType(data.get('type'))
            
            self.metrics['messages_received'] += 1
            
            if message_type == MessageType.SUBSCRIBE:
                await self.handle_subscribe(client_id, data.get('data', {}))
            elif message_type == MessageType.UNSUBSCRIBE:
                await self.handle_unsubscribe(client_id, data.get('data', {}))
            elif message_type == MessageType.PING:
                await self.handle_ping(client_id)
            else:
                # Custom message handlers
                if message_type in self.message_handlers:
                    await self.message_handlers[message_type](client_id, data)
                
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"⚠️  Invalid message from {client_id}: {e}")
            error_msg = WebSocketMessage(
                type=MessageType.ERROR,
                data={"error": "Invalid message format"},
                client_id=client_id
            )
            await self.send_to_client(client_id, error_msg)
    
    async def handle_subscribe(self, client_id: str, data: Dict):
        """Handle subscription request"""
        topics = data.get('topics', [])
        
        if not isinstance(topics, list):
            topics = [topics]
        
        client = self.clients.get(client_id)
        if not client:
            return
        
        for topic in topics:
            # Add client to topic subscription
            if topic not in self.subscriptions:
                self.subscriptions[topic] = set()
            
            self.subscriptions[topic].add(client_id)
            client.subscriptions.add(topic)
            
            logger.debug(f"📡 Client {client_id} subscribed to {topic}")
        
        # Send confirmation
        confirm_msg = WebSocketMessage(
            type=MessageType.SYSTEM_STATUS,
            data={
                "action": "subscribed",
                "topics": topics,
                "total_subscriptions": len(client.subscriptions)
            },
            client_id=client_id
        )
        await self.send_to_client(client_id, confirm_msg)
    
    async def handle_unsubscribe(self, client_id: str, data: Dict):
        """Handle unsubscription request"""
        topics = data.get('topics', [])
        
        if not isinstance(topics, list):
            topics = [topics]
        
        client = self.clients.get(client_id)
        if not client:
            return
        
        for topic in topics:
            # Remove client from topic subscription
            if topic in self.subscriptions:
                self.subscriptions[topic].discard(client_id)
                if not self.subscriptions[topic]:
                    del self.subscriptions[topic]
            
            client.subscriptions.discard(topic)
            
            logger.debug(f"📡 Client {client_id} unsubscribed from {topic}")
        
        # Send confirmation
        confirm_msg = WebSocketMessage(
            type=MessageType.SYSTEM_STATUS,
            data={
                "action": "unsubscribed",
                "topics": topics,
                "total_subscriptions": len(client.subscriptions)
            },
            client_id=client_id
        )
        await self.send_to_client(client_id, confirm_msg)
    
    async def handle_ping(self, client_id: str):
        """Handle ping message"""
        client = self.clients.get(client_id)
        if client:
            client.last_ping = datetime.now()
            
            pong_msg = WebSocketMessage(
                type=MessageType.PONG,
                data={"server_time": datetime.now().isoformat()},
                client_id=client_id
            )
            await self.send_to_client(client_id, pong_msg)
    
    async def send_to_client(self, client_id: str, message: WebSocketMessage) -> bool:
        """Send message to specific client"""
        client = self.clients.get(client_id)
        if not client or client.status != ConnectionStatus.CONNECTED:
            return False
        
        try:
            await client.websocket.send(message.to_json())
            self.metrics['messages_sent'] += 1
            return True
            
        except websockets.exceptions.ConnectionClosed:
            await self.disconnect_client(client_id)
            return False
        except Exception as e:
            logger.error(f"❌ Error sending to client {client_id}: {e}")
            self.metrics['errors'] += 1
            return False
    
    async def broadcast_to_topic(self, topic: str, message: WebSocketMessage):
        """Broadcast message to all subscribers of a topic"""
        if topic not in self.subscriptions:
            return
        
        subscribers = list(self.subscriptions[topic])
        if not subscribers:
            return
        
        logger.debug(f"📢 Broadcasting to {len(subscribers)} subscribers of {topic}")
        
        # Send to all subscribers
        tasks = []
        for client_id in subscribers:
            tasks.append(self.send_to_client(client_id, message))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_sends = sum(1 for result in results if result is True)
        self.metrics['broadcasts'] += 1
        
        logger.debug(f"📊 Broadcast complete: {successful_sends}/{len(subscribers)} successful")
    
    async def broadcast_to_all(self, message: WebSocketMessage):
        """Broadcast message to all connected clients"""
        if not self.clients:
            return
        
        logger.debug(f"📢 Broadcasting to all {len(self.clients)} clients")
        
        tasks = []
        for client_id in list(self.clients.keys()):
            tasks.append(self.send_to_client(client_id, message))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        successful_sends = sum(1 for result in results if result is True)
        
        self.metrics['broadcasts'] += 1
        logger.debug(f"📊 Global broadcast: {successful_sends}/{len(self.clients)} successful")
    
    async def disconnect_client(self, client_id: str):
        """Disconnect and cleanup client"""
        client = self.clients.get(client_id)
        if not client:
            return
        
        # Remove from all subscriptions
        for topic in list(client.subscriptions):
            if topic in self.subscriptions:
                self.subscriptions[topic].discard(client_id)
                if not self.subscriptions[topic]:
                    del self.subscriptions[topic]
        
        # Remove client
        del self.clients[client_id]
        self.metrics['active_connections'] = len(self.clients)
        
        logger.info(f"🔌 Client {client_id} disconnected and cleaned up")
    
    async def disconnect_all_clients(self):
        """Disconnect all clients gracefully"""
        if not self.clients:
            return
        
        logger.info(f"🔌 Disconnecting {len(self.clients)} clients...")
        
        # Send disconnect notification
        disconnect_msg = WebSocketMessage(
            type=MessageType.SYSTEM_STATUS,
            data={"status": "server_shutdown"},
        )
        
        tasks = []
        for client_id in list(self.clients.keys()):
            tasks.append(self.send_to_client(client_id, disconnect_msg))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Close connections
        for client in list(self.clients.values()):
            try:
                await client.websocket.close()
            except:
                pass
        
        self.clients.clear()
        self.subscriptions.clear()
        self.metrics['active_connections'] = 0
    
    async def broadcast_worker(self):
        """Background worker for processing broadcast queue"""
        logger.info("🔄 Broadcast worker started")
        
        while self.is_running:
            try:
                # Wait for broadcast message
                topic, message = await self.broadcast_queue.get()
                await self.broadcast_to_topic(topic, message)
                self.broadcast_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Broadcast worker error: {e}")
                await asyncio.sleep(1)
    
    async def health_check_worker(self):
        """Background worker for health checks"""
        logger.info("🔄 Health check worker started")
        
        while self.is_running:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self.perform_health_check()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Health check worker error: {e}")
    
    async def perform_health_check(self):
        """Perform health check on all connections"""
        self.last_health_check = datetime.now()
        stale_threshold = datetime.now() - timedelta(seconds=self.ping_interval * 3)
        
        stale_clients = []
        for client_id, client in self.clients.items():
            if client.last_ping < stale_threshold:
                stale_clients.append(client_id)
        
        # Disconnect stale clients
        for client_id in stale_clients:
            logger.warning(f"⚠️  Disconnecting stale client: {client_id}")
            await self.disconnect_client(client_id)
        
        if stale_clients:
            logger.info(f"🧹 Health check: removed {len(stale_clients)} stale connections")
    
    def add_message_handler(self, message_type: MessageType, handler: Callable):
        """Add custom message handler"""
        self.message_handlers[message_type] = handler
        logger.info(f"📝 Added message handler for {message_type.value}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get WebSocket server status"""
        uptime = None
        if self.metrics['uptime_start']:
            uptime = (datetime.now() - self.metrics['uptime_start']).total_seconds()
        
        return {
            "is_running": self.is_running,
            "host": self.host,
            "port": self.port,
            "active_connections": len(self.clients),
            "total_subscriptions": sum(len(subs) for subs in self.subscriptions.values()),
            "available_topics": list(self.subscriptions.keys()),
            "uptime_seconds": uptime,
            "metrics": self.metrics.copy(),
            "last_health_check": self.last_health_check.isoformat(),
            "websockets_available": HAS_WEBSOCKETS
        }
    
    def get_connection_info(self) -> List[Dict[str, Any]]:
        """Get detailed connection information"""
        connections = []
        for client_id, client in self.clients.items():
            connections.append({
                "client_id": client_id,
                "connected_at": client.connected_at.isoformat(),
                "last_ping": client.last_ping.isoformat(),
                "subscriptions": list(client.subscriptions),
                "status": client.status.value
            })
        return connections

# Global WebSocket Manager
websocket_manager = None

async def get_websocket_manager() -> WebSocketManager:
    """Get or create global WebSocket manager"""
    global websocket_manager
    if websocket_manager is None:
        websocket_manager = WebSocketManager()
    return websocket_manager

# Convenience functions for stock updates
async def broadcast_stock_update(symbol: str, stock_data: Dict):
    """Broadcast stock price update"""
    manager = await get_websocket_manager()
    
    message = WebSocketMessage(
        type=MessageType.STOCK_UPDATE,
        data={
            "symbol": symbol,
            "stock_data": stock_data,
            "update_type": "price_change"
        }
    )
    
    await manager.broadcast_queue.put((f"stock:{symbol}", message))

async def broadcast_portfolio_update(client_id: str, portfolio_data: Dict):
    """Broadcast portfolio update to specific client"""
    manager = await get_websocket_manager()
    
    message = WebSocketMessage(
        type=MessageType.PORTFOLIO_UPDATE,
        data=portfolio_data,
        client_id=client_id
    )
    
    await manager.send_to_client(client_id, message)

async def main():
    """Test und Demo Funktion"""
    print("🚀 WebSocket Real-time Updates Test")
    print("=" * 50)
    
    if not HAS_WEBSOCKETS:
        print("❌ WebSockets library not available. Install with: pip install websockets")
        return
    
    manager = WebSocketManager(port=8765)
    
    try:
        # Start server
        success = await manager.start_server()
        if not success:
            return
        
        print(f"✅ WebSocket server running on ws://{manager.host}:{manager.port}")
        print("📊 Server Status:")
        status = manager.get_status()
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        # Simulate some updates
        print("\n🔄 Simulating stock updates...")
        for i in range(5):
            await broadcast_stock_update("SAP.DE", {
                "price": 145.50 + i,
                "change": f"+{i*0.5:.2f}",
                "volume": 1000000 + i*10000
            })
            await asyncio.sleep(2)
        
        # Keep server running
        print("\n⏳ Server running... Press Ctrl+C to stop")
        while manager.is_running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🔴 Stopping server...")
    finally:
        await manager.stop_server()

if __name__ == "__main__":
    asyncio.run(main())