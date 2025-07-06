"""
User service for handling user-related business logic.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from src.database.db_access import DBAccess
from src.security.auth_utils import hash_password, verify_password
from src.models.api_models import UserCreate, UserResponse
from src.config.config import Config

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user management operations."""
    
    def __init__(self, db_access: DBAccess):
        """
        Initialize UserService with database access.
        
        Args:
            db_access: Database access layer instance
        """
        self.db_access = db_access
    
    async def create_user(self, user_data: UserCreate) -> Optional[UserResponse]:
        """
        Create a new user with proper password hashing.
        
        Args:
            user_data: User creation data
            
        Returns:
            UserResponse if successful, None if username already exists
            
        Raises:
            ValueError: If user data is invalid
        """
        try:
            # Always hash passwords for security
            hashed_password = hash_password(user_data.password)
            
            # Create user in database
            user_dict = await self.db_access.create_user(
                username=user_data.username,
                hashed_password=hashed_password
            )
            
            if user_dict is None:
                logger.warning(f"Failed to create user: username '{user_data.username}' already exists")
                return None
                
            # Convert to response model
            return UserResponse(
                id=user_dict["id"],
                username=user_dict["username"],
                created_at=user_dict["created_at"],
                last_login=user_dict.get("last_login")
            )
            
        except Exception as e:
            logger.error(f"Error creating user '{user_data.username}': {str(e)}")
            raise
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with username and password.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User data if authentication successful, None otherwise
        """
        try:
            user = await self.db_access.get_user_by_username(username)
            if not user:
                logger.warning(f"Authentication failed: user '{username}' not found")
                return None
            
            # Handle development vs production password verification
            env = Config.get("environment", "development")
            
            if env == "development":
                # Check if this is the dev admin user
                dev_admin_username = Config.get("users", {}).get("admin", {}).get("username")
                dev_admin_password = Config.get("users", {}).get("admin", {}).get("password")
                
                if username == dev_admin_username and password == dev_admin_password:
                    logger.info(f"Development admin user '{username}' authenticated")
                    return user
                else:
                    # For other users in development, verify hashed password
                    if verify_password(password, user["hashed_password"]):
                        logger.info(f"User '{username}' authenticated successfully")
                        return user
            else:
                # Production: always verify hashed password
                if verify_password(password, user["hashed_password"]):
                    logger.info(f"User '{username}' authenticated successfully")
                    return user
            
            logger.warning(f"Authentication failed for user '{username}': invalid password")
            return None
            
        except Exception as e:
            logger.error(f"Error authenticating user '{username}': {str(e)}")
            return None
    
    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            UserResponse if found, None otherwise
        """
        try:
            user_dict = await self.db_access.get_user_by_id(user_id)
            if not user_dict:
                return None
                
            return UserResponse(
                id=user_dict["id"],
                username=user_dict["username"],
                created_at=user_dict["created_at"],
                last_login=user_dict.get("last_login")
            )
            
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            raise
    
    async def get_all_users(self) -> List[UserResponse]:
        """
        Get all users (admin only).
        
        Returns:
            List of UserResponse objects
        """
        try:
            users = await self.db_access.get_all_users()
            return [
                UserResponse(
                    id=user["id"],
                    username=user["username"],
                    created_at=user["created_at"],
                    last_login=user.get("last_login")
                )
                for user in users
            ]
            
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            raise
    
    async def delete_user(self, user_id: int) -> bool:
        """
        Delete user by ID (admin only).
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if user was deleted, False if not found
        """
        try:
            result = await self.db_access.delete_user(user_id)
            if result:
                logger.info(f"User with ID {user_id} deleted successfully")
            else:
                logger.warning(f"User with ID {user_id} not found for deletion")
            return result
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise
    
    def is_admin_user(self, user: Dict[str, Any]) -> bool:
        """
        Check if user has admin privileges.
        
        Args:
            user: User data dictionary
            
        Returns:
            True if user is admin, False otherwise
        """
        try:
            env = Config.get("environment", "development")
            
            if env == "development":
                # In development, check if user is the configured dev admin
                dev_admin_username = Config.get("users", {}).get("admin", {}).get("username")
                return user["username"] == dev_admin_username
            else:
                # In production, first registered user (ID=1) is admin
                # TODO: Implement proper role-based access control
                return user["id"] == 1
                
        except Exception as e:
            logger.error(f"Error checking admin status for user {user.get('id')}: {str(e)}")
            return False