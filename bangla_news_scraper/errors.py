class ScraperError(Exception):
    """Base error for scraper failures."""


class SourceNotSupportedError(ScraperError):
    """Raised when a requested news source is unknown."""


class JobNotFoundError(Exception):
    """Raised when a job cannot be found in the store."""


class JobQueueFullError(Exception):
    """Raised when the job queue is at capacity."""
