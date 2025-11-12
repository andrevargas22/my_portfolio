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
import argparse

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

    # List of YouTube channels to subscribe to (renewal path used by GitHub Actions)
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


def unsubscribe_from_youtube_channels(channels_to_unsubscribe):
    """Perform WebSub unsubscription for provided channels.

    Args:
        channels_to_unsubscribe (list[dict]): List of dicts with keys 'name' and 'channel_id'.
    Returns:
        bool: True if all unsubscription requests accepted (202) else False.
    """
    hub_url = "https://pubsubhubbub.appspot.com/subscribe"
    callback_url = "https://andrevargas.com.br/websub/callback"

    webhook_secret = os.getenv("WEBHOOK_HMAC_SECRET")
    if not webhook_secret:
        logging.error("WEBHOOK_HMAC_SECRET not configured - aborting unsubscribe (expects signed context)")
        return False

    if not channels_to_unsubscribe:
        logging.info("No channels provided to unsubscribe.")
        return True

    all_successful = True
    for channel in channels_to_unsubscribe:
        try:
            topic_url = f"https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel['channel_id']}"
            unsubscribe_data = {
                "hub.callback": callback_url,
                "hub.topic": topic_url,
                "hub.verify": "async",
                "hub.mode": "unsubscribe",
                # Secret can still be sent for symmetry (ignored in lease logic)
                "hub.secret": webhook_secret,
            }
            response = requests.post(hub_url, data=unsubscribe_data, timeout=15)
            if response.status_code == 202:
                logging.info(f"{channel['name']}: Unsubscribe request accepted")
            else:
                logging.error(f"{channel['name']}: Unsubscribe failed (HTTP {response.status_code})")
                all_successful = False
        except Exception as e:
            logging.error(f"{channel['name']}: Error during unsubscribe ({str(e)})")
            all_successful = False

    return all_successful


def parse_args():
    parser = argparse.ArgumentParser(
        description="Manage YouTube WebSub subscriptions (default: subscribe/renew).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--unsub",
        action="store_true",
        help="Run in unsubscribe mode (dry-run by default – real call line is commented).",
    )
    return parser.parse_args()


def main():
    """Main execution function with optional unsubscribe mode."""
    args = parse_args()

    # Empty placeholder list for manual unsubscription (populate when needed)
    channels_to_unsubscribe = [
        # Example structure:
        # {"name": "Some Channel", "channel_id": "UCxxxxxxxxxxxxxxxxx"},
    ]

    try:
        if args.unsub:
            logging.info("Running in --unsub mode (no network calls executed by default).")
            logging.info("Populate 'channels_to_unsubscribe' list in the script to target channels.")
            # To actually execute unsubscription requests, uncomment the following line:
            # success = unsubscribe_from_youtube_channels(channels_to_unsubscribe)
            # For now we simulate success so you can test the flag wiring.
            success = True
        else:
            success = subscribe_to_youtube_channels()
        sys.exit(0 if success else 1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
