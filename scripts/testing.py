"""
WebSub notification handler for YouTube video processing.

This module receives YouTube WebSub notifications and dispatches
them to GitHub Actions for processing.
"""

import csv
import io
import os
import time
import logging
import re
import hmac
import hashlib
import requests
import xml.etree.ElementTree as ET
import jwt
import threading
from datetime import datetime, timezone, timedelta


# ==================== Pipeline Logger ====================

class PipelineLogger:
    """Writes pipeline events to GitHub Gist CSV log."""
    
    def __init__(self, gist_id: str, github_token: str):
        """
        Initialize logger with Gist credentials.
        
        Args:
            gist_id: GitHub Gist ID (LOG_GIST_ID)
            github_token: GitHub Personal Access Token (GH_PAT)
        """
        self.gist_id = gist_id
        self.headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self.gist_filename = "pipelog.csv"
        self.brasilia_tz = timezone(timedelta(hours=-3))
        self.fieldnames = ["video_id", "channel", "title", "status", "timestamp", "info", "env"]
    
    def _read_csv(self) -> list[dict]:
        """Read current CSV content from Gist."""
        try:
            response = requests.get(
                f"https://api.github.com/gists/{self.gist_id}",
                headers=self.headers,
                timeout=10,
            )
            
            if response.status_code != 200:
                return []
            
            content = response.json()["files"][self.gist_filename]["content"]
            return list(csv.DictReader(io.StringIO(content)))
        
        except Exception as e:
            logging.warning(f"[Logger] Error reading gist: {e}")
            return []
    
    def _write_csv(self, rows: list[dict]) -> bool:
        """Write CSV content back to Gist."""
        try:
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
            response = requests.patch(
                f"https://api.github.com/gists/{self.gist_id}",
                headers=self.headers,
                json={"files": {self.gist_filename: {"content": output.getvalue()}}},
                timeout=10,
            )
            
            return response.status_code == 200
        
        except Exception as e:
            logging.warning(f"[Logger] Error writing gist: {e}")
            return False
    
    def log(self, video_id: str, channel: str, title: str, status: str, info: str = "") -> bool:
        """
        Append a status entry to the pipeline log.
        
        Args:
            video_id: YouTube video ID
            channel: Channel name
            title: Video title
            status: Status code (e.g., 'notification_received', 'dispatch_sent')
            info: Optional additional information
            
        Returns:
            bool: True if log was written successfully
        """
        timestamp = datetime.now(self.brasilia_tz).strftime("%d/%m/%Y %H:%M:%S")
        
        # Read existing rows
        rows = self._read_csv()
        
        # Append new row
        rows.append({
            "video_id": video_id,
            "channel": channel,
            "title": title,
            "status": status,
            "timestamp": timestamp,
            "info": info,
            "env": "prd",
        })
        
        # Write back to Gist
        return self._write_csv(rows)


def log_pipeline_event(video_id: str, channel: str, title: str, status: str, info: str = "") -> bool:
    """
    Helper function to log pipeline events.
    
    Args:
        video_id: YouTube video ID
        channel: Channel name
        title: Video title
        status: Status code
        info: Optional additional information
        
    Returns:
        bool: True if logged successfully
    """
    gist_id = os.getenv("LOG_GIST_ID")
    gh_token = os.getenv("GH_PAT")
    
    if not gist_id or not gh_token:
        logging.debug("[Logger] LOG_GIST_ID or GH_PAT not configured - skipping log")
        return False
    
    try:
        logger = PipelineLogger(gist_id, gh_token)
        return logger.log(video_id, channel, title, status, info)
    except Exception as e:
        logging.warning(f"[Logger] Failed to log event: {e}")
        return False


# ==================== Utility Functions ====================


def parse_youtube_notification(xml_data):
    """
    Parse XML notification from YouTube WebSub.
    
    Args:
        xml_data: Raw XML bytes from WebSub POST request
        
    Returns:
        dict: Video metadata (video_id, title, url, channel, published) or None on error
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


def verify_webhook_signature(body: bytes, signature_header: str) -> bool:
    """
    Verify HMAC-SHA1 signature from WebSub notification.

    Args:
        body: Raw request body as bytes
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
            webhook_secret.encode("utf-8"), body, hashlib.sha1
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


def process_video_in_background(video_data: dict, is_youtube: bool) -> None:
    """
    Process video notification in background thread (after WebSub response).
    
    Simple workflow:
    1. Log notification receipt
    2. Trigger GitHub Actions workflow (all processing happens there)
    
    Args:
        video_data: Parsed video data
        is_youtube: True if notification from YouTube, False if manual test
    """
    try:
        source_label = "REAL VIDEO" if is_youtube else "TEST VIDEO"
        
        # Log video details
        logging.info(f"########### [{source_label} NOTIFICATION] ###########")
        logging.info(f"Video ID: {video_data['video_id']}")
        logging.info(f"Channel: {video_data['channel']}")
        logging.info(f"Title: {video_data['title']}")
        logging.info(f"Link: {video_data['url']}")
        logging.info(f"Published: {video_data['published']}")
        logging.info("#" * 50)
        
        # Log notification receipt
        log_pipeline_event(
            video_data['video_id'],
            video_data['channel'],
            video_data['title'],
            "notification_received"
        )
        
        # Trigger GitHub Actions workflow
        # All processing (validation, filtering, download, transcription) happens in Actions
        logging.info("[Background] Triggering GitHub Actions workflow...")
        trigger_video_processing_workflow(video_data)
        
        log_pipeline_event(
            video_data['video_id'],
            video_data['channel'],
            video_data['title'],
            "dispatch_sent"
        )
        
        logging.info("[Background] Dispatch completed successfully")
        
    except Exception as e:
        logging.error(f"[Background] Error dispatching workflow: {e}", exc_info=True)
        try:
            log_pipeline_event(
                video_data.get('video_id', 'unknown'),
                video_data.get('channel', 'unknown'),
                video_data.get('title', 'unknown'),
                "dispatch_failed",
                info=str(e)
            )
        except:
            pass


def trigger_video_processing_workflow(video_data):
    """
    Dispatch a workflow event to GitHub Actions for video processing.
    
    Args:
        video_data: Video metadata dict (video_id, url, title, channel, published_at)
    """
    if not video_data or video_data.get("video_id") in (None, "Unknown"):
        logging.error("[GitHub] Missing or invalid video data")
        return

    if not _valid_video_id(video_data.get("video_id", "")):
        logging.error("[GitHub] Video ID pattern invalid - aborting dispatch")
        return

    repo_owner = "andrevargas22"
    repo_name = "Colorado_IA"
    token = _get_dispatch_token()
    if not token:
        return

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dispatches"
    
    # Build payload - video processing happens in GitHub Actions
    client_payload = {
        "video_id": video_data["video_id"],
        "video_url": video_data["url"],
        "title": video_data["title"],
        "channel": video_data["channel"],
        "published_at": video_data["published"],
    }
    
    payload = {
        "event_type": "video_published",
        "client_payload": client_payload,
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
    # Log all incoming requests for debugging
    user_agent = request_headers.get('User-Agent', 'Unknown') if request_headers else 'Unknown'
    is_youtube = 'FeedFetcher-Google' in user_agent
    source_type = "🔴 REAL (YouTube)" if is_youtube else "🧪 TEST (Manual)"
    
    logging.info(f"[WebSub] {source_type} {request_method} request from: {user_agent}")
    
    if request_method == "GET":
        challenge = request_args.get("hub.challenge") if request_args else None
        mode = request_args.get("hub.mode") if request_args else None
        topic = request_args.get("hub.topic") if request_args else None

        logging.info(f"[WebSub] GET request - Mode: {mode}, Topic: {topic}")

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
                logging.info(f"[WebSub] Video parsed successfully, dispatching to background thread...")
                
                # Start background processing thread (non-blocking)
                thread = threading.Thread(
                    target=process_video_in_background,
                    args=(video_data, is_youtube),
                    daemon=False  # Thread continues after request ends
                )
                thread.start()
                
                logging.info(f"[WebSub] Background thread started, returning OK to YouTube")

        except ET.ParseError as e:
            logging.error(f"[WebSub] XML ParseError processing notification: {e}")
        except Exception as e:
            logging.error(f"[WebSub] Error parsing notification: {e}", exc_info=True)

        
        return "OK"

    # Method not supported
    return "Method not allowed", 405
