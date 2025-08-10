#!/usr/bin/env python3
"""
Startup script for the 6MLET Tech Challenge Delivery 01 application.
"""

import os
import uvicorn
from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app.api.main:app", host="0.0.0.0", port=port, reload=True, log_level="info"
    )
