from enum import Enum


class MediaQuality(Enum):
    thumbnail = "thumbnail"
    original = "original"
    high = "high"


class MediaQualityCompression(Enum):
    thumbnail = 25
    original = 100
    high = 85
