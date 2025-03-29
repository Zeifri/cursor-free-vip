import os
import sys
import configparser
from colorama import Fore, Style
from utils import get_user_documents_path, get_default_chrome_path, get_linux_cursor_path

EMOJI = {
    "INFO": "ℹ️",
    "WARNING": "⚠️",
    "ERROR": "❌",
    "SUCCESS": "✅",
    "ADMIN": "🔒",
    "ARROW": "➡️",
    "USER": "👤",
    "KEY": "🔑",
    "SETTINGS": "⚙️"
}

def setup_config(translator=None):
    """Setup configuration file and return config object"""
    try:
        config_dir = os.path.join(get_user_documents_path(), ".cursor-free-vip")
        config_file = os.path.join(config_dir, "config.ini")
        os.makedirs(config_dir, exist_ok=True)
        
        config = configparser.ConfigParser()
        
        # Default configuration
        default_config = {
            'Chrome': {
                'chromepath': get_default_chrome_path()
            },
            'Turnstile': {
                'handle_turnstile_time': '2',
                'handle_turnstile_random_time': '1-3'
            },
            'Timing': {
                'min_random_time': '0.1',
                'max_random_time': '0.8',
                'page_load_wait': '0.1-0.8',
                'input_wait': '0.3-0.8',
                'submit_wait': '0.5-1.5',
                'verification_code_input': '0.1-0.3',
                'verification_success_wait': '2-3',
                'verification_retry_wait': '2-3',
                'email_check_initial_wait': '4-6',
                'email_refresh_wait': '2-4',
                'settings_page_load_wait': '1-2',
                'failed_retry_time': '0.5-1',
                'retry_interval': '8-12',
                'max_timeout': '160'
            },
            'Utils': {
                'enabled_update_check': 'True',
                'enabled_account_info': 'True'
            }
        }

        # Add system-specific path configuration
        if sys.platform == "win32":
            appdata = os.getenv("APPDATA")
            localappdata = os.getenv("LOCALAPPDATA", "")
            default_config['WindowsPaths'] = {
                'storage_path': os.path.join(appdata, "Cursor", "User", "globalStorage", "storage.json"),
                'sqlite_path': os.path.join(appdata, "Cursor", "User", "globalStorage", "state.vscdb"),
                'machine_id_path': os.path.join(appdata, "Cursor", "machineId"),
                'cursor_path': os.path.join(localappdata, "Programs", "Cursor", "resources", "app"),
                'updater_path': os.path.join(localappdata, "cursor-updater"),
                'update_yml_path': os.path.join(localappdata, "Programs", "Cursor", "resources", "app-update.yml")
            }
        elif sys.platform == "darwin":
            default_config['MacPaths'] = {
                'storage_path': os.path.abspath(os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/storage.json")),
                'sqlite_path': os.path.abspath(os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/state.vscdb")),
                'machine_id_path': os.path.expanduser("~/Library/Application Support/Cursor/machineId"),
                'cursor_path': "/Applications/Cursor.app/Contents/Resources/app",
                'updater_path': os.path.expanduser("~/Library/Application Support/cursor-updater"),
                'update_yml_path': "/Applications/Cursor.app/Contents/Resources/app-update.yml"
            }
        elif sys.platform == "linux":
            sudo_user = os.environ.get('SUDO_USER')
            actual_home = f"/home/{sudo_user}" if sudo_user else os.path.expanduser("~")
            
            default_config['LinuxPaths'] = {
                'storage_path': os.path.abspath(os.path.join(actual_home, ".config/cursor/User/globalStorage/storage.json")),
                'sqlite_path': os.path.abspath(os.path.join(actual_home, ".config/cursor/User/globalStorage/state.vscdb")),
                'machine_id_path': os.path.expanduser("~/.config/cursor/machineid"),
                'cursor_path': get_linux_cursor_path(),
                'updater_path': os.path.expanduser("~/.config/cursor-updater"),
                'update_yml_path': "/Applications/Cursor.app/Contents/Resources/app-update.yml"
            }

        # Read existing configuration and merge
        if os.path.exists(config_file):
            config.read(config_file, encoding='utf-8')
            config_modified = False
            
            for section, options in default_config.items():
                if not config.has_section(section):
                    config.add_section(section)
                    config_modified = True
                for option, value in options.items():
                    if not config.has_option(section, option):
                        config.set(section, option, str(value))
                        config_modified = True
                        if translator:
                            print(f"{Fore.YELLOW}ℹ️ {translator.get('register.config_option_added', option=f'{section}.{option}')}{Style.RESET_ALL}")

            if config_modified:
                with open(config_file, 'w', encoding='utf-8') as f:
                    config.write(f)
                if translator:
                    print(f"{Fore.GREEN}✅ {translator.get('register.config_updated')}{Style.RESET_ALL}")
        else:
            for section, options in default_config.items():
                config.add_section(section)
                for option, value in options.items():
                    config.set(section, option, str(value))

            with open(config_file, 'w', encoding='utf-8') as f:
                config.write(f)
            if translator:
                print(f"{Fore.GREEN}✅ {translator.get('register.config_created')}: {config_file}{Style.RESET_ALL}")

        return config

    except Exception as e:
        if translator:
            print(f"{Fore.RED}❌ {translator.get('register.config_setup_error', error=str(e))}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Error setting up config: {e}{Style.RESET_ALL}")
        return None
    
def print_config(config, translator=None):
    """Print configuration in a readable format"""
    if not config:
        print(f"{Fore.YELLOW}{EMOJI['WARNING']} {translator.get('config.config_not_available')}{Style.RESET_ALL}")
        return
        
    print(f"\n{Fore.CYAN}{EMOJI['INFO']} {translator.get('config.configuration')}:{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")
    for section in config.sections():
        print(f"{Fore.GREEN}[{section}]{Style.RESET_ALL}")
        for key, value in config.items(section):
            # 对布尔值进行特殊处理，使其显示为彩色
            if value.lower() in ('true', 'yes', 'on', '1'):
                value_display = f"{Fore.GREEN}{translator.get('config.enabled')}{Style.RESET_ALL}"
            elif value.lower() in ('false', 'no', 'off', '0'):
                value_display = f"{Fore.RED}{translator.get('config.disabled')}{Style.RESET_ALL}"
            else:
                value_display = value
                
            print(f"  {key} = {value_display}")
    
    print(f"\n{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")
    config_dir = os.path.join(get_user_documents_path(), ".cursor-free-vip", "config.ini")
    print(f"{Fore.CYAN}{EMOJI['INFO']} {translator.get('config.config_directory')}: {config_dir}{Style.RESET_ALL}")

    print()  

def get_config(translator=None):
    """Get existing config or create new one"""
    return setup_config(translator) 