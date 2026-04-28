#!/usr/bin/env python3
"""
WebSub Debugging and Diagnostic Tool

This script helps diagnose WebSub subscription issues by:
1. Testing endpoint accessibility
2. Verifying HMAC signature validation
3. Checking subscription status
4. Re-subscribing to channels if needed
"""

import os
import sys
import logging
import requests
import hmac
import hashlib
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def test_endpoint_accessibility(callback_url):
    """
    Test if the WebSub callback endpoint is publicly accessible.
    
    Args:
        callback_url: The callback URL to test
        
    Returns:
        bool: True if endpoint is accessible
    """
    logging.info(f"Testing endpoint accessibility: {callback_url}")
    
    try:
        # Test GET with a fake challenge (should return 'OK' or challenge)
        response = requests.get(
            callback_url,
            params={"hub.challenge": "test_challenge_12345"},
            timeout=10
        )
        
        if response.status_code == 200:
            logging.info(f"✅ Endpoint is accessible (Status: 200)")
            logging.info(f"   Response: {response.text[:100]}")
            return True
        else:
            logging.error(f"❌ Endpoint returned status {response.status_code}")
            return False
            
    except requests.RequestException as e:
        logging.error(f"❌ Failed to reach endpoint: {e}")
        return False


def test_hmac_signature():
    """
    Test HMAC signature generation and validation logic.
    
    Returns:
        bool: True if HMAC secret is configured correctly
    """
    logging.info("Testing HMAC signature configuration...")
    
    webhook_secret = os.getenv("WEBHOOK_HMAC_SECRET")
    if not webhook_secret:
        logging.error("❌ WEBHOOK_HMAC_SECRET not configured!")
        return False
    
    # Test signature generation
    test_data = b"test_payload_data"
    signature = hmac.new(
        webhook_secret.encode("utf-8"),
        test_data,
        hashlib.sha1
    ).hexdigest()
    
    logging.info(f"✅ HMAC secret configured (length: {len(webhook_secret)})")
    logging.info(f"   Sample signature: sha1={signature[:20]}...")
    return True


def check_subscription_status(channels):
    """
    Attempt to check if subscriptions are active by making a test subscription request.
    
    Note: WebSub hub doesn't provide a direct way to check status,
    so we'll just attempt to re-subscribe and check the response.
    
    Args:
        channels: List of channel dictionaries with 'name' and 'channel_id'
        
    Returns:
        dict: Status for each channel
    """
    logging.info("Checking/Renewing subscriptions...")
    
    hub_url = "https://pubsubhubbub.appspot.com/subscribe"
    callback_url = "https://andrevargas.com.br/websub/callback"
    webhook_secret = os.getenv("WEBHOOK_HMAC_SECRET")
    
    if not webhook_secret:
        logging.error("Cannot check subscriptions without WEBHOOK_HMAC_SECRET")
        return {}
    
    results = {}
    
    for channel in channels:
        try:
            topic_url = f"https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel['channel_id']}"
            
            subscription_data = {
                "hub.callback": callback_url,
                "hub.topic": topic_url,
                "hub.verify": "async",
                "hub.mode": "subscribe",
                "hub.lease_seconds": "864000",  # 10 days for more frequent renewal
                "hub.secret": webhook_secret,
            }
            
            response = requests.post(hub_url, data=subscription_data, timeout=15)
            
            if response.status_code == 202:
                logging.info(f"✅ {channel['name']}: Subscription request accepted")
                results[channel['name']] = "success"
            else:
                logging.error(f"❌ {channel['name']}: Failed (HTTP {response.status_code})")
                logging.error(f"   Response: {response.text}")
                results[channel['name']] = f"failed_{response.status_code}"
                
        except Exception as e:
            logging.error(f"❌ {channel['name']}: Error - {e}")
            results[channel['name']] = f"error_{str(e)}"
    
    return results


def main():
    """Main diagnostic routine."""
    
    print("=" * 70)
    print("WebSub Diagnostic Tool")
    print(f"Run at: {datetime.now().isoformat()}")
    print("=" * 70)
    print()
    
    # Channels to monitor
    channels = [
        {"name": "Lucas Collar", "channel_id": "UCAh4Y2AOSMwmatv9ktmhAAQ"},
        {"name": "Alexandre Ernst", "channel_id": "UCBgSy_cNIoGYnyLjmKHQOAg"},
        {"name": "Lucas Dias", "channel_id": "UCIMDIPyS1vsHBa4t9wlN8IQ"},
        {"name": "Canal do Vaguinha", "channel_id": "UCkoqa3e5oFNkEGvgrxLAmrQ"},
    ]
    
    # Run diagnostics
    endpoint_ok = test_endpoint_accessibility("https://andrevargas.com.br/websub/callback")
    print()
    
    hmac_ok = test_hmac_signature()
    print()
    
    subscription_results = check_subscription_status(channels)
    print()
    
    # Summary
    print("=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)
    print(f"Endpoint Accessible: {'✅ YES' if endpoint_ok else '❌ NO'}")
    print(f"HMAC Configured: {'✅ YES' if hmac_ok else '❌ NO'}")
    print()
    print("Subscription Status:")
    for channel, status in subscription_results.items():
        icon = "✅" if status == "success" else "❌"
        print(f"  {icon} {channel}: {status}")
    print("=" * 70)
    
    # Exit code
    all_ok = endpoint_ok and hmac_ok and all(s == "success" for s in subscription_results.values())
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
