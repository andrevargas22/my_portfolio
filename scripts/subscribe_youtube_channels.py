#!/usr/bin/env python3
"""
YouTube Channel WebSub Subscription Manager

This script automatically subscribes to YouTube channels via WebSub (PubSubHubbub) 
for real-time video notifications. This is part of an ongoing LLM project.

Author: André Vargas
"""

import os
import sys
import logging
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def subscribe_to_youtube_channels():
    """
    Automatically subscribes to all YouTube channels of interest via WebSub.
    
    Returns:
        bool: True if all subscriptions were successful, False otherwise.
    """
    
    # List of YouTube channels to subscribe to
    channels_to_subscribe = [
        {
            "name": "Lucas Collar",
            "channel_id": "UCAh4Y2AOSMwmatv9ktmhAAQ"
        },
        {
            "name": "Alexandre Ernst",
            "channel_id": "UCBgSy_cNIoGYnyLjmKHQOAg"
        },
        {
            "name": "Lucas Dias",
            "channel_id": "UCIMDIPyS1vsHBa4t9wlN8IQ"
        },
        {
            "name": "Canal do Vaguinha",
            "channel_id": "UCkoqa3e5oFNkEGvgrxLAmrQ"
        },
        {
            "name": "A Dupla",
            "channel_id": "UCRbfE8wK0_f5BPXtH424G_Q"
        },
        {
            "name": "JB Filho Repórter",
            "channel_id": "UCkPxmeuHR2EJR8DJpX8utMQ"
        }
    ]
    
    hub_url = "https://pubsubhubbub.appspot.com/subscribe"
    callback_url = "https://andrevargas.com.br/websub/callback"
    all_successful = True
    
    for channel in channels_to_subscribe:
        try:
            topic_url = f"https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel['channel_id']}"
            
            subscription_data = {
                'hub.callback': callback_url,
                'hub.topic': topic_url,
                'hub.verify': 'async',
                'hub.mode': 'subscribe',
                'hub.lease_seconds': '2764800'
            }
            
            response = requests.post(hub_url, data=subscription_data, timeout=15)
            
            if response.status_code == 202:
                logging.info(f"{channel['name']}: Success")
            else:
                logging.error(f"{channel['name']}: Failed (HTTP {response.status_code})")
                all_successful = False
                
        except Exception as e:
            logging.error(f"{channel['name']}: Error ({str(e)})")
            all_successful = False
    
    return all_successful

def main():
    """Main execution function"""
    try:
        success = subscribe_to_youtube_channels()
        sys.exit(0 if success else 1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
