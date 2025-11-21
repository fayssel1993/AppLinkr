from datetime import datetime
import pytz
from flask import Flask, request
import requests
from user_agents import parse


### User Information
def get_client_ip():
    """Get the client IP address."""
    if 'X-Forwarded-For' in request.headers:
        ip_address = request.headers['X-Forwarded-For'].split(',')[0]
        print(ip_address, flush=True)
    else:
        ip_address = request.remote_addr
    return ip_address




def get_location(ip_address):
    """Get the approximate location of the user from their IP address."""
    try:
        response = requests.get(f'http://ipinfo.io/{ip_address}/json')
        data = response.json()
        return f"{data['city']}, {data['region']}, {data['country']}"
    except Exception as e:
        print(f"Error fetching location for IP {ip_address}: {e}")
        return "Unknown"
    


def detect_browser_and_os(user_agent):
    """Detect browser and operating system from User-Agent."""
    if not user_agent:
        return "Unknown", "Unknown"

    try:
        ua = parse(user_agent)
        browser = f"{ua.browser.family} {ua.browser.version_string}"
        os = f"{ua.os.family} {ua.os.version_string}"
        return browser, os
    except Exception:
        return "Unknown", "Unknown"


def detect_device(user_agent):
    """Detect the device based on the User-Agent string."""
    if not user_agent:
        return "unknown"

    ua = parse(user_agent)

    def flag_true(obj, *names):
        """Return True if any named boolean attribute exists and is truthy."""
        for name in names:
            if getattr(obj, name, False):
                return True
        return False

    # Prefer explicit platform flags when available (development branch support)
    if flag_true(ua, "is_android", "is_android_device"):
        return "android"
    if flag_true(ua, "is_ios", "is_ios_device"):
        return "ios"

    os_family = (getattr(ua, "os", None) and ua.os.family or "").lower()
    device_family = (getattr(ua, "device", None) and ua.device.family or "").lower()

    if "android" in os_family or "android" in device_family:
        return "android"
    if os_family in ("ios", "ipados") or device_family in ("iphone", "ipad", "ipod"):
        return "ios"

    # Fallback for uncommon or unparsed strings
    if "android" in user_agent:
        return "android"
    if any(ios_hint in user_agent for ios_hint in ("iphone", "ipad", "ipod", "ios")):
        return "ios"

    return "unknown"
    
def get_access_time(ip_address=None):
    """Get current timestamp in user's local timezone for access_time field."""
    try:
        # Get current UTC time
        utc_now = datetime.now(pytz.UTC)
        
        # Try to get timezone from IP location if provided
        if ip_address:
            try:
                response = requests.get(f'http://ipinfo.io/{ip_address}/json')
                data = response.json()
                if 'timezone' in data:
                    # Get local time in user's timezone
                    user_tz = pytz.timezone(data['timezone'])
                    local_time = utc_now.astimezone(user_tz)
                    # Return in SQLite DATETIME format
                    return local_time.strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                print(f"Error fetching timezone for IP {ip_address}: {e}")
        
        # Fallback to UTC time in SQLite DATETIME format
        return utc_now.strftime("%Y-%m-%d %H:%M:%S")
        
    except Exception as e:
        print(f"Error getting access time: {e}")
        # Return current UTC time as fallback
        return datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
