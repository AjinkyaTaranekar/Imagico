from enum import Enum


class MediaQuality(Enum):
    thumbnail = "thumbnail"
    original = "original"


class MediaQualityCompression(Enum):
    thumbnail = 25
    original = 100
