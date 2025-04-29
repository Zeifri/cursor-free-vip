from abc import ABC, abstractmethod

class EmailTabInterface(ABC):
    """Email tab interface for handling email verification"""
    
    @abstractmethod
    def refresh_inbox(self) -> None:
        """Refresh the email inbox"""
        pass
    
    @abstractmethod
    def check_for_cursor_email(self) -> bool:
        """Check if there is a verification email from Cursor
        
        Returns:
            bool: True if verification email exists, False otherwise
        """
        pass
    
    @abstractmethod
    def get_verification_code(self) -> str:
        """Get the verification code from the email
        
        Returns:
            str: The verification code if found, empty string otherwise
        """
        pass
