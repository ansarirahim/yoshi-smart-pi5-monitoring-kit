#!/usr/bin/env python3
"""
Camera Connection Test Script.

Tests various URL patterns and password combinations for Tuya/ICSee cameras.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
"""

import requests
from requests.auth import HTTPBasicAuth
import sys
from typing import List, Tuple, Optional


def test_url(url: str, username: str, password: str, timeout: int = 5) -> Tuple[bool, str]:
    """
    Test a camera URL with given credentials.
    
    Args:
        url: Camera URL to test
        username: Camera username
        password: Camera password
        timeout: Request timeout in seconds
    
    Returns:
        Tuple of (success, message)
    """
    try:
        print(f"\nTesting: {url}")
        print(f"  Username: {username}")
        print(f"  Password: {'(blank)' if not password else password}")
        
        # Try with authentication
        if username:
            response = requests.get(
                url,
                auth=HTTPBasicAuth(username, password),
                timeout=timeout,
                stream=True
            )
        else:
            response = requests.get(url, timeout=timeout, stream=True)
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            print(f"  ✅ SUCCESS! Status: {response.status_code}")
            print(f"  Content-Type: {content_type}")
            return True, f"Success with {username}/{password or '(blank)'}"
        else:
            print(f"  ❌ Failed: Status {response.status_code}")
            return False, f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        print(f"  ❌ Timeout")
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Connection failed")
        return False, "Connection failed"
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False, str(e)


def main():
    """Main test function."""
    print("=" * 70)
    print("CAMERA CONNECTION TEST")
    print("=" * 70)
    
    # Get camera IP from user
    if len(sys.argv) > 1:
        camera_ip = sys.argv[1]
    else:
        camera_ip = input("\nEnter camera IP address (e.g., 192.168.1.100): ").strip()
    
    if not camera_ip:
        print("Error: No IP address provided")
        sys.exit(1)
    
    print(f"\nCamera IP: {camera_ip}")
    
    # URL patterns to test (from Yoshinori's message)
    url_patterns = [
        f"http://{camera_ip}:88/cgi-bin/snapshot.cgi?channel=0",
        f"http://{camera_ip}:80/video/mjpeg.cgi",
        f"http://{camera_ip}:80/cgi-bin/mjpg/video.cgi",
        f"http://{camera_ip}:88/video/mjpeg.cgi",
        f"http://{camera_ip}/snapshot.cgi",
    ]
    
    # Password combinations to test (from Yoshinori's message)
    credentials = [
        ("admin", ""),        # blank password
        ("admin", "12345"),   # common default
        ("admin", "admin"),   # common default
    ]
    
    print("\n" + "=" * 70)
    print("TESTING URL PATTERNS")
    print("=" * 70)
    
    successful_configs = []
    
    # Test each URL with each credential combination
    for url in url_patterns:
        for username, password in credentials:
            success, message = test_url(url, username, password)
            if success:
                successful_configs.append({
                    'url': url,
                    'username': username,
                    'password': password,
                    'message': message
                })
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    if successful_configs:
        print(f"\n✅ Found {len(successful_configs)} working configuration(s):\n")
        for i, config in enumerate(successful_configs, 1):
            print(f"{i}. URL: {config['url']}")
            print(f"   Username: {config['username']}")
            print(f"   Password: {config['password'] or '(blank)'}")
            print()
        
        print("\n📝 RECOMMENDED .env CONFIGURATION:")
        print("-" * 70)
        best = successful_configs[0]
        print(f"CAMERA_URL={best['url']}")
        print(f"CAMERA_USERNAME={best['username']}")
        print(f"CAMERA_PASSWORD={best['password']}")
        print("-" * 70)
        
    else:
        print("\n❌ No working configuration found.")
        print("\nTroubleshooting:")
        print("1. Verify camera IP address is correct")
        print("2. Ensure camera is powered on and connected to network")
        print("3. Check if camera is on same network as your computer")
        print("4. Try accessing camera web interface in browser")
        print("5. Consider USB capture card fallback option")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

