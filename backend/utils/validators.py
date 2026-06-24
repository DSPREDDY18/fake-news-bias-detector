"""Input validation helpers."""
from __future__ import annotations

import re
from typing import Optional
from backend.utils.errors import ValidationError


def validate_article_text(text: Optional[str]) -> str:
    """Validate and normalise article text.

    Args:
        text: The raw article text submitted by the user.

    Returns:
        The stripped and validated text.

    Raises:
        ValidationError: If the text is missing, too short, or too long.
    """
    if not text or not isinstance(text, str):
        raise ValidationError('Article text is required.')

    text = text.strip()

    if len(text) < 50:
        raise ValidationError(
            f'Article text must be at least 50 characters long (got {len(text)}).'
        )

    if len(text) > 50_000:
        raise ValidationError(
            'Article text must not exceed 50,000 characters.'
        )

    return text


_URL_PATTERN = re.compile(
    r'^https?://'                          # scheme
    r'(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)*'  # subdomains
    r'[A-Za-z]{2,}'                        # TLD
    r'(?::\d{1,5})?'                       # optional port
    r'(?:/[^\s]*)?$',                       # path
    re.IGNORECASE,
)


def validate_url(url: Optional[str]) -> str:
    """Validate a URL string.

    Args:
        url: The URL to validate.

    Returns:
        The stripped, validated URL.

    Raises:
        ValidationError: If the URL is missing or malformed.
    """
    if not url or not isinstance(url, str):
        raise ValidationError('URL is required.')

    url = url.strip()

    if not _URL_PATTERN.match(url):
        raise ValidationError('Please provide a valid URL starting with http:// or https://.')

    return url


_EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)


def validate_email(email: Optional[str]) -> str:
    """Validate an e-mail address.

    Args:
        email: The email to validate.

    Returns:
        The stripped, lower-cased email.

    Raises:
        ValidationError: If the email is missing or malformed.
    """
    if not email or not isinstance(email, str):
        raise ValidationError('Email is required.')

    email = email.strip().lower()

    if not _EMAIL_PATTERN.match(email):
        raise ValidationError('Please provide a valid email address.')

    return email


def validate_password(password: Optional[str]) -> str:
    """Validate a password meets complexity requirements.

    Requirements:
        - At least 8 characters
        - Contains at least one letter
        - Contains at least one digit

    Args:
        password: The plaintext password to validate.

    Returns:
        The validated password (unchanged).

    Raises:
        ValidationError: If the password does not meet requirements.
    """
    if not password or not isinstance(password, str):
        raise ValidationError('Password is required.')

    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')

    if not re.search(r'[A-Za-z]', password):
        raise ValidationError('Password must contain at least one letter.')

    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one digit.')

    return password
