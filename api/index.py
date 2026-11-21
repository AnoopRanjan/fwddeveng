"""
Vercel Serverless Function Entrypoint
Loads the Flask app from the root directory.
"""

import os
import sys

# Add project root directory to sys.path so modules can be imported seamlessly
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

# Vercel WSGI entrypoint expects the Flask instance named 'app'
# This is already provided by 'from app import app'
