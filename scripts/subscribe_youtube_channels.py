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
from datetime import datetime

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
    
    logging.info(f"🚀 Starting subscription process for {len(channels_to_subscribe)} channels...")
    
    subscription_results = []
    hub_url = "https://pubsubhubbub.appspot.com/subscribe"
    callback_url = "https://andrevargas.com.br/websub/callback"
    
    for channel in channels_to_subscribe:
        try:
            logging.info(f"📺 Subscribing to: {channel['name']} ({channel['channel_id']})")
            
            topic_url = f"https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel['channel_id']}"
            
            # WebSub subscription payload
            subscription_data = {
                'hub.callback': callback_url,
                'hub.topic': topic_url,
                'hub.verify': 'async',
                'hub.mode': 'subscribe',
                'hub.lease_seconds': '2764800'  # 32 days for complete month coverage
            }
            
            # Send subscription request to WebSub hub
            response = requests.post(hub_url, data=subscription_data, timeout=15)
            
            if response.status_code == 202:
                subscription_results.append({
                    "channel_name": channel["name"],
                    "channel_id": channel["channel_id"],
                    "status": "success",
                    "response_code": response.status_code
                })
                logging.info(f"✅ Successfully subscribed to {channel['name']}")
            else:
                subscription_results.append({
                    "channel_name": channel["name"],
                    "channel_id": channel["channel_id"],
                    "status": "failed",
                    "response_code": response.status_code,
                    "response_text": response.text[:200] if response.text else "No response text"
                })
                logging.error(f"❌ Failed to subscribe to {channel['name']}: HTTP {response.status_code}")
                
        except Exception as e:
            subscription_results.append({
                "channel_name": channel["name"],
                "channel_id": channel["channel_id"],
                "status": "error",
                "error": str(e)
            })
            logging.error(f"💥 Exception while subscribing to {channel['name']}: {e}")
    
    # Calculate and display summary statistics
    successful_subscriptions = len([result for result in subscription_results if result["status"] == "success"])
    total_channels = len(channels_to_subscribe)
    failed_subscriptions = total_channels - successful_subscriptions
    success_rate = (successful_subscriptions/total_channels)*100
    
    logging.info("=" * 60)
    logging.info("📊 SUBSCRIPTION SUMMARY")
    logging.info("=" * 60)
    logging.info(f"📺 Total channels: {total_channels}")
    logging.info(f"✅ Successful subscriptions: {successful_subscriptions}")
    logging.info(f"❌ Failed subscriptions: {failed_subscriptions}")
    logging.info(f"📈 Success rate: {success_rate:.1f}%")
    logging.info("=" * 60)
    
    # Display detailed results for failed subscriptions
    if failed_subscriptions > 0:
        logging.warning("❌ FAILED SUBSCRIPTIONS DETAILS:")
        for result in subscription_results:
            if result["status"] != "success":
                error_msg = result.get('error', f'HTTP {result.get("response_code", "Unknown")}')
                logging.warning(f"  • {result['channel_name']}: {error_msg}")
    
    # Return success status
    all_successful = failed_subscriptions == 0
    if all_successful:
        logging.info("🎉 All channel subscriptions completed successfully!")
    else:
        logging.warning(f"⚠️  {failed_subscriptions} subscription(s) failed. Check logs above for details.")
    
    return all_successful

def main():
    """Main execution function"""
    try:
        logging.info(f"🔔 YouTube Channel WebSub Subscription Manager")
        logging.info(f"⏰ Execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        success = subscribe_to_youtube_channels()
        
        if success:
            logging.info("✅ Script completed successfully!")
            sys.exit(0)
        else:
            logging.error("❌ Script completed with errors!")
            sys.exit(1)
            
    except Exception as e:
        logging.error(f"💥 Unexpected error in main execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
