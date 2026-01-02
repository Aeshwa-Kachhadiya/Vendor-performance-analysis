"""
Vendor Analytics Pipeline Package
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .pipeline import run_pipeline
from .watcher import start_watcher

__all__ = ['run_pipeline', 'start_watcher']
