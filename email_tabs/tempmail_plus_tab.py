import requests
import re
from typing import Optional
from .email_tab_interface import EmailTabInterface

class TempMailPlusTab(EmailTabInterface):
    """Implementation of EmailTabInterface for tempmail.plus"""
    
    def __init__(self, email: str, epin: str):
        """Initialize TempMailPlusTab
        
        Args:
            email: The email address to check
            epin: The epin token for authentication
        """
        self.email = email
        self.epin = epin
        self.base_url = "https://tempmail.plus/api"
        self.headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://tempmail.plus/zh/',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        self.cookies = {'email': email}
        self._cached_mail_id = None  # 缓存mail_id
        
    def refresh_inbox(self) -> None:
        """Refresh the email inbox"""
        pass
            
    def check_for_cursor_email(self) -> bool:
        """Check if there is a verification email from Cursor
        
        Returns:
            bool: True if verification email exists, False otherwise
        """
        try:
            params = {
                'email': self.email,
                'epin': self.epin
            }
            response = requests.get(
                f"{self.base_url}/mails",
                params=params,
                headers=self.headers,
                cookies=self.cookies
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get('result') and data.get('mail_list'):
                for mail in data['mail_list']:
                    if 'cursor.sh' in mail.get('from_mail', '') and mail.get('is_new') == True:
                        self._cached_mail_id = mail.get('mail_id')  # 缓存mail_id
                        return True
            return False
        except Exception as e:
            print(f"检查Cursor邮件失败: {str(e)}")
            return False
            
    def get_verification_code(self) -> str:
        """Get the verification code from the email
        
        Returns:
            str: The verification code if found, empty string otherwise
        """
        try:
            # 如果没有缓存的mail_id，先检查是否有新邮件
            if not self._cached_mail_id:
                if not self.check_for_cursor_email():
                    return ""
                    
            # 使用缓存的mail_id获取邮件内容
            params = {
                'email': self.email,
                'epin': self.epin
            }
            response = requests.get(
                f"{self.base_url}/mails/{self._cached_mail_id}",
                params=params,
                headers=self.headers,
                cookies=self.cookies
            )
            response.raise_for_status()
            
            data = response.json()
            if not data.get('result'):
                return ""
                
            # Extract verification code from text content using regex
            text = data.get('text', '')
            match = re.search(r'\n\n(\d{6})\n\n', text)
            if match:
                return match.group(1)
                
            return ""
        except Exception as e:
            print(f"获取验证码失败: {str(e)}")
            return "" 