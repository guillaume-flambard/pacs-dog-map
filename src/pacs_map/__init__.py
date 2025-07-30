"""
PACS Dog Map - Animal Sterilization Tracking System
A community-focused tool for tracking dogs and cats that need sterilization
"""

__version__ = "1.0.0"
__author__ = "PACS Koh Phangan Volunteers"
__email__ = "info@pacsthailand.com"

from .core import PacsMapGenerator
from .data import DataManager
from .coordinates import CoordinateExtractor

__all__ = ['PacsMapGenerator', 'DataManager', 'CoordinateExtractor']