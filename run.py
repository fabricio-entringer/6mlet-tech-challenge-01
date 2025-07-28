#!/usr/bin/env python3
"""
Startup script for the 6MLET Tech Challenge Delivery 01 application.
"""

import uvicorn
from app import app

if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )