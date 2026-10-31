"""
Vercel entrypoint for UNIYO LMS.
Deliberately imports `server` (not `cloud_server`) to avoid:
  - wiping active_sessions on every cold start
  - starting the Telegram bot polling thread
  - chmod'ing directories on Vercel's read-only FS
"""
import os
os.environ.setdefault("VERCEL", "1")
os.environ.setdefault("SESSION_BACKEND", "cookie")

from server import app  # noqa: F401
