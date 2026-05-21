"""
Testing and experimental features for my portfolio website.
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
import tempfile
from pathlib import Path
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
            status: Status code (e.g., 'pipeline_start', 'download_success')
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


def sanitize_filename(name: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters.
    
    Args:
        name: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Remove invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Remove emojis and special unicode characters
    name = re.sub(r'[^\x00-\x7F]+', '', name)
    # Collapse multiple underscores
    name = re.sub(r'_+', '_', name)
    # Remove leading/trailing underscores
    name = name.strip('_')
    return name or "unknown"


def download_audio_ytdlp(video_id: str, video_url: str) -> Path | None:
    """
    Download audio from YouTube using yt-dlp.
    
    Args:
        video_id: YouTube video ID
        video_url: Full YouTube video URL
        
    Returns:
        Path: Path to downloaded MP3 file, or None on failure
    """
    import yt_dlp

    class YtdlpLogger:
        def debug(self, msg):
            if msg.startswith('[debug] '):
                return
            logging.info(f"[yt-dlp] {msg}")
        def warning(self, msg):
            logging.warning(f"[yt-dlp] {msg}")
        def error(self, msg):
            logging.error(f"[yt-dlp] {msg}")

    cookies_file = None

    try:
        # Create temporary directory for download
        temp_dir = Path(tempfile.mkdtemp(prefix="ytdlp_"))
        logging.info(f"[Download] Starting yt-dlp download for video_id={video_id}")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(temp_dir / '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'logger': YtdlpLogger(),
        }

        youtube_cookies_b64 = os.getenv("YOUTUBE_COOKIES_B64")
        if youtube_cookies_b64:
            # Cloud/datacenter IPs: use cookies + web client (needs Node.js 20+ for n-challenge)
            import base64
            cookies_file = Path(tempfile.mktemp(suffix=".txt", prefix="yt_cookies_"))
            cookies_file.write_bytes(base64.b64decode(youtube_cookies_b64))
            ydl_opts['cookiefile'] = str(cookies_file)
            ydl_opts['js_runtimes'] = {'node': {}}
            ydl_opts['remote_components'] = ['ejs:github']
            logging.info("[Download] Cloud mode: using cookies for authentication")
        else:
            # Local/residential IPs: android/ios clients bypass bot detection without cookies
            ydl_opts['extractor_args'] = {'youtube': {'player_client': ['android', 'ios']}}
            logging.info("[Download] Local mode: using android/ios client")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            
            mp3_path = temp_dir / f"{video_id}.mp3"
            
            if not mp3_path.exists():
                logging.error(f"[Download] Expected file not found: {mp3_path}")
                return None
            
            file_size_mb = mp3_path.stat().st_size / (1024 * 1024)
            duration_sec = info.get('duration', 0)
            
            logging.info(f"[Download] Success - {file_size_mb:.2f} MB, {duration_sec}s")
            return mp3_path
            
    except Exception as e:
        logging.error(f"[Download] Failed: {e}")
        return None
    finally:
        if 'cookies_file' in dir() and cookies_file and cookies_file.exists():
            cookies_file.unlink()


def upload_audio_to_gcs(local_path: Path, channel: str, published_at: str, video_id: str) -> str | None:
    """
    Upload audio file to Google Cloud Storage.
    
    Args:
        local_path: Local path to audio file
        channel: Channel name
        published_at: Publication timestamp
        video_id: YouTube video ID
        
    Returns:
        str: GCS path if successful, None otherwise
    """
    try:
        from google.cloud import storage
        
        bucket_name = os.getenv("GCS_BUCKET_NAME")
        if not bucket_name:
            logging.error("[GCS] GCS_BUCKET_NAME not configured")
            return None
        
        # Generate GCS path: <channel>/<timestamp>_<video_id>/audio.mp3
        channel_sanitized = sanitize_filename(channel)
        
        # Parse timestamp
        try:
            dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            timestamp = dt.strftime("%Y-%m-%d_%H-%M-%S")
        except:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Create directory structure: channel/timestamp_videoid/audio.mp3
        video_dir = f"{timestamp}_{video_id}"
        gcs_path = f"{channel_sanitized}/{video_dir}/audio.mp3"
        
        logging.info(f"[GCS] Uploading to gs://{bucket_name}/{gcs_path}")
        
        # Upload
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(gcs_path)
        
        blob.upload_from_filename(str(local_path))
        
        logging.info("[GCS] Upload successful")
        return gcs_path
        
    except Exception as e:
        logging.error(f"[GCS] Upload failed: {e}")
        return None


def send_telegram_notification(title: str, channel: str, url: str) -> bool:
    """
    Send a simple Telegram notification about a new video.
    
    Args:
        title: Video title
        channel: Channel name
        url: Video URL
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not telegram_token or not telegram_chat_id:
        logging.warning("[Telegram] Bot token or chat ID not configured - skipping notification")
        return False
    
    try:
        message = f"Novo video\n\nCanal: {channel}\nTitulo: {title}\nLink: {url}"
        
        response = requests.post(
            f"https://api.telegram.org/bot{telegram_token}/sendMessage",
            data={
                "chat_id": telegram_chat_id,
                "text": message,
            },
            timeout=10,
        )
        
        if response.status_code == 200:
            logging.info("[Telegram] Notification sent successfully")
            return True
        else:
            logging.error(f"[Telegram] Failed to send notification: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logging.error(f"[Telegram] Error sending notification: {e}")
        return False


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


def check_video_availability(video_id: str) -> tuple[bool, dict]:
    """
    Check if a YouTube video is ready for download using YouTube Data API v3.
    
    Returns True only if ALL conditions are met:
    - uploadStatus == "processed"
    - liveBroadcastContent == "none"
    - privacyStatus == "public"
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        tuple: (is_ready: bool, status_details: dict)
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        logging.warning("[YouTube API] YOUTUBE_API_KEY not configured - skipping availability check")
        return True, {}  # Assume ready if API key not configured
    
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "status,snippet",
        "id": video_id,
        "key": api_key
    }
    
    try:
        r = requests.get(url, params=params, timeout=10)
        
        if r.status_code != 200:
            logging.warning(f"[YouTube API] HTTP {r.status_code} - assuming video ready")
            return True, {}
        
        data = r.json()
        
        if not data.get("items"):
            logging.warning(f"[YouTube API] Video {video_id} not found")
            return False, {"error": "video_not_found"}
        
        item = data["items"][0]
        upload_status = item.get("status", {}).get("uploadStatus")
        live_status = item.get("snippet", {}).get("liveBroadcastContent")
        privacy_status = item.get("status", {}).get("privacyStatus")
        
        status_details = {
            "uploadStatus": upload_status,
            "liveBroadcastContent": live_status,
            "privacyStatus": privacy_status,
        }
        
        is_ready = (
            upload_status == "processed"
            and live_status == "none"
            and privacy_status == "public"
        )
        
        # Log detailed status
        if is_ready:
            logging.info(f"[YouTube API] Video {video_id} is ready")
        else:
            logging.warning(
                f"[YouTube API] Video {video_id} not ready - "
                f"upload={upload_status}, live={live_status}, privacy={privacy_status}"
            )
        
        return is_ready, status_details
        
    except Exception as e:
        logging.error(f"[YouTube API] Error checking video {video_id}: {e}")
        return True, {"error": str(e)}  # Don't block on API errors


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


def should_filter_video(video_data: dict) -> tuple[bool, str]:
    """
    Determine if a video should be filtered (ignored) based on content rules.
    
    Args:
        video_data: Dict with 'url', 'channel', 'title' keys
        
    Returns:
        tuple: (should_filter: bool, reason: str)
    """
    url = video_data.get("url", "")
    channel = video_data.get("channel", "")
    title = video_data.get("title", "")
    
    # Filter 1: YouTube Shorts
    if "/shorts/" in url:
        logging.info(f"[Filter] IGNORED: YouTube Short detected")
        return True, "YouTube Short"
    
    # Filter 2: Canal "A Dupla" + "Hora da Dupla"
    if channel == "A Dupla" and "Hora da Dupla" in title:
        logging.info(f"[Filter] [IGNORED: A Dupla - Hora da Dupla")
        return True, "A Dupla - Hora da Dupla"
    
    # Filter 3: Canal "A Dupla" + título começa com "🔵⚫️" (Grêmio)
    if channel == "A Dupla" and title.startswith("🔵⚫️"):
        logging.info(f"[Filter] IGNORED: A Dupla - Grêmio content")
        return True, "A Dupla - Conteudo Gremio"
    
    # Filter 4: Alexandre Ernst + "INTERVENÇÃO #"
    if channel == "Alexandre Ernst" and "INTERVENÇÃO #" in title:
        logging.info(f"[Filter] IGNORED: Alexandre Ernst - INTERVENÇÃO")
        return True, "Alexandre Ernst - INTERVENCAO"
    
    # Filter 5: Collar Repórter + specific programs
    if channel == "Collar Repórter":
        ignored_programs = ["INTERVALO DO COLLAR", "PÓS-JOGO", "LIVE DO COLLAR"]
        for program in ignored_programs:
            if program in title:
                logging.info(f"[Filter] ⏭IGNORED: Collar Repórter - {program}")
                return True, f"Collar Reporter - {program}"
    
    # Video passes all filters - should be processed
    logging.info(f"[Filter] PASSED: Video will be processed")
    return False, ""


def process_video_in_background(video_data: dict, is_youtube: bool) -> None:
    """
    Process video in background thread (after WebSub response).
    
    Full workflow:
    1. Check video availability (YouTube API)
    2. Apply content filters
    3. Download audio with yt-dlp
    4. Upload to GCS
    5. Trigger GitHub Actions workflow
    
    Args:
        video_data: Parsed video data
        is_youtube: True if notification from YouTube, False if manual test
    """
    audio_path = None
    try:
        source_label = "REAL VIDEO" if is_youtube else "TEST VIDEO"
        
        # Log video details
        logging.info(f"########### [{source_label} PARSED - BACKGROUND] ###########")
        logging.info(f"Link: {video_data['url']}")
        logging.info(f"Channel: {video_data['channel']}")
        logging.info(f"Title: {video_data['title']}")
        logging.info(f"Published at: {video_data['published']}")
        logging.info("######################################")
        
        # Log pipeline start
        log_pipeline_event(
            video_data['video_id'],
            video_data['channel'],
            video_data['title'],
            "pipeline_start"
        )
        
        # Step 1: Check video availability
        is_available, status_details = check_video_availability(video_data['video_id'])
        
        # Send Telegram notification with availability status
        status_msg = "Video disponivel" if is_available else "Video nao disponivel"
        if status_details:
            status_msg += f"\n\nuploadStatus: {status_details.get('uploadStatus', 'N/A')}"
            status_msg += f"\nliveBroadcastContent: {status_details.get('liveBroadcastContent', 'N/A')}"
            status_msg += f"\nprivacyStatus: {status_details.get('privacyStatus', 'N/A')}"
            if "error" in status_details:
                status_msg += f"\nErro: {status_details['error']}"
        send_telegram_notification(video_data['title'], video_data['channel'], status_msg)
        
        # Log availability check result
        if is_available:
            log_pipeline_event(
                video_data['video_id'],
                video_data['channel'],
                video_data['title'],
                "video_ready",
                info=str(status_details)
            )
        else:
            log_pipeline_event(
                video_data['video_id'],
                video_data['channel'],
                video_data['title'],
                "video_not_ready",
                info=str(status_details)
            )
            logging.warning(f"[Background] ⏭️  Video not ready - aborting processing")
            return
        
        # Step 2: Apply content filters
        should_filter, filter_reason = should_filter_video(video_data)
        if should_filter:
            log_pipeline_event(
                video_data['video_id'],
                video_data['channel'],
                video_data['title'],
                "video_filtered",
                info=filter_reason
            )
            send_telegram_notification(
                video_data['title'],
                video_data['channel'],
                f"Video ignorado\n\nMotivo: {filter_reason}"
            )
            logging.info(f"[Background] ⏭️  Video filtered - aborting processing")
            return
        
        # Step 3: Download audio with yt-dlp
        logging.info(f"[Background] Starting audio download...")
        audio_path = download_audio_ytdlp(video_data['video_id'], video_data['url'])
        
        if not audio_path:
            log_pipeline_event(
                video_data['video_id'],
                video_data['channel'],
                video_data['title'],
                "download_failed"
            )
            send_telegram_notification(
                video_data['title'],
                video_data['channel'],
                "Download falhou"
            )
            logging.error(f"[Background] Download failed - aborting processing")
            return
        
        log_pipeline_event(
            video_data['video_id'],
            video_data['channel'],
            video_data['title'],
            "download_success"
        )
        send_telegram_notification(
            video_data['title'],
            video_data['channel'],
            "Download concluido"
        )
        
        # Step 4: Upload to GCS
        gcs_path = upload_audio_to_gcs(
            audio_path,
            video_data['channel'],
            video_data['published'],
            video_data['video_id']
        )
        
        if not gcs_path:
            log_pipeline_event(
                video_data['video_id'],
                video_data['channel'],
                video_data['title'],
                "gcs_upload_failed"
            )
            send_telegram_notification(
                video_data['title'],
                video_data['channel'],
                "Upload GCS falhou"
            )
            logging.error(f"[Background] GCS upload failed - aborting processing")
            return
        
        log_pipeline_event(
            video_data['video_id'],
            video_data['channel'],
            video_data['title'],
            "gcs_upload_success",
            info=gcs_path
        )
        send_telegram_notification(
            video_data['title'],
            video_data['channel'],
            f"Upload GCS concluido\n\nPath: {gcs_path}"
        )
        
        # Step 5: Trigger workflow with audio ready flag
        logging.info("[Background] Audio ready")
        trigger_video_processing_workflow(video_data, audio_ready=True, gcs_path=gcs_path)
        
        logging.info("[Background] Processing completed")
        
    except Exception as e:
        logging.error(f"[Background] Error processing video: {e}", exc_info=True)
        # Log pipeline failure
        try:
            log_pipeline_event(
                video_data.get('video_id', 'unknown'),
                video_data.get('channel', 'unknown'),
                video_data.get('title', 'unknown'),
                "pipeline_failed",
                info=str(e)
            )
        except:
            pass
        # Processing aborted due to error
    finally:
        # Cleanup temporary file
        if audio_path and audio_path.exists():
            try:
                audio_path.unlink()
                if audio_path.parent.name.startswith("ytdlp_"):
                    audio_path.parent.rmdir()
                logging.info(f"[Background] Cleanup: Removed temporary file")
            except Exception as e:
                logging.warning(f"[Background] Cleanup failed: {e}")


def trigger_video_processing_workflow(video_data, audio_ready=False, gcs_path=None):
    """
    Dispatch a workflow event in the target repository using a GitHub App token.
    
    Args:
        video_data: Video metadata dict
        audio_ready: Whether audio is already downloaded and uploaded to GCS
        gcs_path: GCS path to audio file (if audio_ready=True)
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
    
    # Build payload with audio status
    client_payload = {
        "video_id": video_data["video_id"],
        "video_url": video_data["url"],
        "title": video_data["title"],
        "channel": video_data["channel"],
        "published_at": video_data["published"],
        "audio_ready": audio_ready,
    }
    
    # Add GCS path if audio is ready
    if audio_ready and gcs_path:
        client_payload["gcs_path"] = gcs_path
    
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
                # Send immediate Telegram notification (before any filtering/processing)
                send_telegram_notification(
                    title=video_data["title"],
                    channel=video_data["channel"],
                    url=video_data["url"]
                )
                
                logging.info(f"[WebSub] Video parsed successfully, starting background processing...")
                
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
