"""
Testing and experimental features for my portfolio website.
"""

import os
import time
import logging
import re
import hmac
import hashlib
import requests
import xml.etree.ElementTree as ET
import jwt


def parse_youtube_notification(xml_data):
    """
    Parses the XML notification from YouTube WebSub.
    """
    try:
        # Parse the XML
        root = ET.fromstring(xml_data)

        # Namespaces YouTube/Atom
        namespaces = {
            "atom": "http://www.w3.org/2005/Atom",
            "yt": "http://www.youtube.com/xml/schemas/2015",
        }

        # Get video entry
        entry = root.find("atom:entry", namespaces)
        if entry is None:
            logging.error("[Parse] No entry found in XML")
            return None

        # Extract video information
        video_id = entry.find("yt:videoId", namespaces)
        title = entry.find("atom:title", namespaces)
        link = entry.find('atom:link[@rel="alternate"]', namespaces)
        author = entry.find("atom:author/atom:name", namespaces)
        published = entry.find("atom:published", namespaces)

        # Build video data
        video_data = {
            "video_id": video_id.text.strip()
            if video_id is not None and video_id.text
            else "Unknown",
            "title": title.text.strip()
            if title is not None and title.text
            else "No title",
            "url": link.get("href")
            if link is not None
            else f"https://www.youtube.com/watch?v={video_id.text}",
            "channel": author.text.strip()
            if author is not None and author.text
            else "Unknown",
            "published": published.text.strip()
            if published is not None and published.text
            else "Unknown",
        }

        logging.info(f"Video Data: {video_data}")

        return video_data

    except ET.ParseError as e:
        logging.error(f"[Parse] XML Parse Error: {e}")
        return None
    except Exception as e:
        logging.error(f"[Parse] Unexpected Error: {e}")
        return None


def verify_webhook_signature(body: str, signature_header: str) -> bool:
    """
    Verify HMAC-SHA1 signature from WebSub notification.

    Args:
        body: Raw request body as string
        signature_header: Value of X-Hub-Signature header (e.g., "sha1=abc123...")

    Returns:
        bool: True if signature is valid, False otherwise
    """
    webhook_secret = os.getenv("WEBHOOK_HMAC_SECRET")
    if not webhook_secret:
        logging.warning(
            "[WebSub] HMAC verification requested but WEBHOOK_HMAC_SECRET not configured"
        )
        return False

    try:
        # Parse signature header: "sha1=hexdigest"
        algorithm, provided_signature = signature_header.split("=", 1)
        if algorithm != "sha1":
            logging.error(f"[WebSub] Unsupported signature algorithm: {algorithm}")
            return False

        # Calculate expected signature
        expected_signature = hmac.new(
            webhook_secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha1
        ).hexdigest()

        # Secure comparison to prevent timing attacks
        is_valid = hmac.compare_digest(provided_signature, expected_signature)

        if is_valid:
            logging.info("[WebSub] HMAC signature validated successfully")
        else:
            logging.error("[WebSub] HMAC signature validation failed")

        return is_valid

    except (ValueError, AttributeError) as e:
        logging.error(f"[WebSub] Error parsing signature header: {e}")
        return False


def _load_private_key():
    """
    Get the GitHub App private key from environment variables.
    """
    key = os.getenv("GRENALBOT_PRIVATE_KEY")
    if not key:
        return None
    if "\\n" in key:
        key = key.replace("\\n", "\n")
    return key


def _generate_github_app_jwt(app_id: str, private_key: str) -> str:
    """
    Generate a short-lived JWT for GitHub App authentication.
    """
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + 540, "iss": app_id}
    token = jwt.encode(payload, private_key, algorithm="RS256")
    return token


def _get_installation_token(app_jwt: str, installation_id: str) -> str | None:
    """
    Get an installation access token for a GitHub App.
    """
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github.v3+json",
    }
    try:
        r = requests.post(url, headers=headers, timeout=10)
        if r.status_code == 201:
            data = r.json()
            return data.get("token")
        logging.error(
            f"[GitHub] Failed to get installation token: {r.status_code} {r.text}"
        )
    except Exception as e:
        logging.error(f"[GitHub] Error requesting installation token: {e}")
    return None


def _get_dispatch_token():
    """
    Return an installation access token using GitHub App authentication.
    """
    app_id = os.getenv("GRENALBOT_ID")
    inst_id = os.getenv("GRENALBOT_INSTALLATION_ID")
    private_key = _load_private_key()

    if not all([app_id, inst_id, private_key]):
        logging.error(
            "[GitHub] GitHub App configuration incomplete (missing App ID, Installation ID, or private key)"
        )
        return None

    try:
        app_jwt = _generate_github_app_jwt(app_id, private_key)
        install_token = _get_installation_token(app_jwt, inst_id)
        if install_token:
            return install_token
        logging.error("[GitHub] Failed to obtain installation access token")
        return None
    except Exception as e:
        logging.error(f"[GitHub] GitHub App authentication failed: {e}")
        return None


def _valid_video_id(video_id: str) -> bool:
    """
    Validate YouTube video ID format.
    """
    return bool(re.fullmatch(r"[A-Za-z0-9_-]{6,20}", video_id or ""))


def trigger_video_processing_workflow(video_data):
    """
    Dispatch a workflow event in the target repository using a GitHub App token.
    """
    if not video_data or video_data.get("video_id") in (None, "Unknown"):
        logging.error("[GitHub] Missing or invalid video data")
        return

    if not _valid_video_id(video_data.get("video_id", "")):
        logging.error("[GitHub] Video ID pattern invalid - aborting dispatch")
        return

    repo_owner = "andrevargas22"
    repo_name = "grenalbot"
    token = _get_dispatch_token()
    if not token:
        return

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dispatches"
    payload = {
        "event_type": "video_published",
        "client_payload": {
            "video_id": video_data["video_id"],
            "video_url": video_data["url"],
            "title": video_data["title"],
            "channel": video_data["channel"],
            "published_at": video_data["published"],
        },
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        if r.status_code == 204:
            logging.info(
                f"[GitHub] Workflow dispatch sent for video_id={video_data['video_id']}"
            )
        else:
            logging.error(f"[GitHub] Dispatch failed {r.status_code}: {r.text}")
    except Exception as e:
        logging.error(f"[GitHub] Dispatch error: {e}")


def handle_websub_callback(
    request_method, request_args=None, request_data=None, request_headers=None
):
    """
    Handle WebSub callback for both GET (challenge) and POST (notification) requests.

    Args:
        request_method: HTTP method ('GET' or 'POST')
        request_args: Query parameters for GET requests
        request_data: Body data for POST requests
        request_headers: Request headers

    Returns:
        tuple: (response_body, status_code) or just response_body for 200 OK
    """
    if request_method == "GET":
        challenge = request_args.get("hub.challenge") if request_args else None

        logging.info("[WebSub] GET request received")

        if challenge:
            if re.match(r"^[a-zA-Z0-9_-]{1,128}$", challenge):
                logging.info("[WebSub] Valid Challenge")
                return challenge
            else:
                logging.error("[WebSub] Invalid Challenge")
                return "Invalid challenge", 400

        logging.info("[WebSub] No challenge - Returning OK")
        return "OK"

    elif request_method == "POST":
        logging.info("[WebSub] POST notification received")

        webhook_secret = os.getenv("WEBHOOK_HMAC_SECRET")
        hub_signature = (
            request_headers.get("X-Hub-Signature") if request_headers else None
        )

        # Enforce secret presence (fail closed)
        if not webhook_secret:
            logging.error(
                "[WebSub] WEBHOOK_HMAC_SECRET not configured - rejecting notification"
            )
            return "Server HMAC not configured", 503

        # Require signature header
        if not hub_signature:
            logging.error("[WebSub] Missing X-Hub-Signature header")
            return "Signature required", 401

        # Verify signature
        if not verify_webhook_signature(request_data, hub_signature):
            logging.error("[WebSub] HMAC verification failed - rejecting payload")
            return "Forbidden", 403

        logging.info("[WebSub] HMAC verification successful")

        try:
            video_data = parse_youtube_notification(request_data)
            if video_data:
                logging.info("########### [VIDEO PARSED] ###########")
                logging.info(f"Link: {video_data['url']}")
                logging.info(f"Channel: {video_data['channel']}")
                logging.info(f"Title: {video_data['title']}")
                logging.info(f"Published at: {video_data['published']}")
                logging.info("######################################")

                #trigger_video_processing_workflow(video_data)

        except ET.ParseError as e:
            logging.error(f"[WebSub] XML ParseError processing notification: {e}")
        except requests.RequestException as e:
            logging.error(f"[WebSub] RequestException during video processing workflow: {e}")
        except Exception as e:
            logging.critical(f"[WebSub] Unexpected error processing notification: {e}", exc_info=True)

        
        return "OK"

    # Method not supported
    return "Method not allowed", 405
