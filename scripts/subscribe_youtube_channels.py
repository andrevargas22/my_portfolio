#!/usr/bin/env python3
"""
YouTube Channel WebSub Subscription Manager

This script automatically subscribes to YouTube channels via WebSub (PubSubHubbub)
for real-time video notifications. This is part of an ongoing LLM project.
"""

import os
import sys
import logging
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def subscribe_to_youtube_channels():
    """
    Automatically subscribes to all YouTube channels of interest via WebSub.

    Returns:
        bool: True if all subscriptions were successful, False otherwise.
    """

    # List of YouTube channels to subscribe to
    channels_to_subscribe = [
        {"name": "Lucas Collar", "channel_id": "UCAh4Y2AOSMwmatv9ktmhAAQ"},
        {"name": "Alexandre Ernst", "channel_id": "UCBgSy_cNIoGYnyLjmKHQOAg"},
        {"name": "Lucas Dias", "channel_id": "UCIMDIPyS1vsHBa4t9wlN8IQ"},
        {"name": "Canal do Vaguinha", "channel_id": "UCkoqa3e5oFNkEGvgrxLAmrQ"},
        {"name": "Careca de Saber", "channel_id": "UCUaNjDcaVliZyWd-MgsDAzw"},
        {"name": "César Cidade Dias", "channel_id": "UC-vcAXksTA21wp1iN4ZGv6Q"},
        {"name": "Cristiano Oliveira", "channel_id": "UC66qTkwGt0VOzejqDmzQyjg"},
        {"name": "A Dupla", "channel_id": "UCRbfE8wK0_f5BPXtH424G_Q"},
        {"name": "JB Filho Repórter", "channel_id": "UCkPxmeuHR2EJR8DJpX8utMQ"},
        {"name": "Leonardo Meneghetti", "channel_id": "UCZqLwvgBgcSV5onlSrxkjQQ"},
        {"name": "Marinho Saldanha", "channel_id": "UC7a6C6H12xIAYZUKa_f9GKQ"},
    ]

    hub_url = "https://pubsubhubbub.appspot.com/subscribe"
    callback_url = "https://andrevargas.com.br/websub/callback"

    # Get HMAC secret for WebSub validation
    webhook_secret = os.getenv("WEBHOOK_HMAC_SECRET")
    if not webhook_secret:
        logging.error(
            "WEBHOOK_HMAC_SECRET not configured - aborting (signed notifications required)"
        )
        return False

    all_successful = True

    for channel in channels_to_subscribe:
        try:
            topic_url = f"https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel['channel_id']}"

            subscription_data = {
                "hub.callback": callback_url,
                "hub.topic": topic_url,
                "hub.verify": "async",
                "hub.mode": "subscribe",
                "hub.lease_seconds": "2764800",
                # Always include secret (validated earlier)
                "hub.secret": webhook_secret,
            }

            response = requests.post(hub_url, data=subscription_data, timeout=15)

            if response.status_code == 202:
                logging.info(f"{channel['name']}: Success")
            else:
                logging.error(
                    f"{channel['name']}: Failed (HTTP {response.status_code})"
                )
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
