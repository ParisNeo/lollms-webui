"""
Regression tests for lollms.security path-sanitisation helpers.

Covers GH issue #641: the original `\\.\\.\\.+` pattern required THREE or more
dots and silently allowed the canonical `..` traversal sequence. The current
pattern uses an explicit `\\.{2,}` quantifier; these tests pin that behaviour
so any future "simplification" back to a 3+-dot form fails CI immediately.
"""

import pytest
from fastapi import HTTPException

from lollms.security import sanitize_path, sanitize_path_from_endpoint


# ---------------------------------------------------------------------------
# sanitize_path
# ---------------------------------------------------------------------------

# Each entry is the path that MUST be rejected. The list is intentionally
# exhaustive across the bypasses called out in #641 plus a handful of common
# variations seen in CTF / pentest payloads.
PATH_TRAVERSAL_PAYLOADS = [
    "../etc/passwd",                       # canonical 2-dot — the #641 bypass
    "../../etc/passwd",                    # double traversal
    "../../../../../../etc/shadow",        # deeply nested
    "..",                                  # bare parent
    "../",                                 # bare parent w/ slash
    "foo/../bar",                          # mid-path traversal
    "foo/./../../bar",                     # mixed with current-dir
    "..\\etc\\passwd",                     # Windows-style separator
    "foo\\..\\..\\bar",                    # mixed mid-path Windows
    "..../etc/passwd",                     # 4-dot bypass attempt
    "...../etc/passwd",                    # 5-dot bypass attempt
    "foo//bar",                            # collapsed-separator trick
    "foo///bar",
    "$(whoami)",                           # shell command substitution
    "logs/$(id)/out.txt",
]


@pytest.mark.parametrize("payload", PATH_TRAVERSAL_PAYLOADS)
def test_sanitize_path_rejects_traversal_payload(payload):
    with pytest.raises(HTTPException) as excinfo:
        sanitize_path(payload)
    assert excinfo.value.status_code == 400


SAFE_RELATIVE_PATHS = [
    "models/llama/weights.bin",
    "personalities/coder/config.yaml",
    "a/b/c/d",
    "single_segment",
    "with-dash/and_underscore",
    "file.txt",
    "nested.dir/file.name.ext",            # single dots are fine
]


@pytest.mark.parametrize("path", SAFE_RELATIVE_PATHS)
def test_sanitize_path_accepts_safe_relative(path):
    assert sanitize_path(path) == path


def test_sanitize_path_rejects_absolute_path_by_default():
    with pytest.raises(HTTPException):
        sanitize_path("/etc/passwd")


def test_sanitize_path_rejects_windows_drive_letter_by_default():
    with pytest.raises(HTTPException):
        sanitize_path("C:")


def test_sanitize_path_allows_absolute_when_opted_in():
    # When the caller explicitly opts in, an absolute path is returned
    # untouched (apart from a strip). Traversal sequences are still blocked.
    result = sanitize_path("/var/lib/lollms/cache", allow_absolute_path=True)
    assert result == "/var/lib/lollms/cache"


def test_sanitize_path_allow_absolute_still_blocks_traversal():
    with pytest.raises(HTTPException):
        sanitize_path("/var/lib/../../../etc/passwd", allow_absolute_path=True)


def test_sanitize_path_rejects_current_folder_by_default():
    with pytest.raises(HTTPException):
        sanitize_path("./")


def test_sanitize_path_allows_current_folder_when_opted_in():
    assert sanitize_path("./", allow_current_folder=True) == "./"


def test_sanitize_path_returns_none_for_none():
    assert sanitize_path(None) is None


@pytest.mark.parametrize("ch", list('!"#$%&\'()*+,;<=>?@[]^`{|}~'))
def test_sanitize_path_rejects_unauthorized_punctuation(ch):
    with pytest.raises(HTTPException):
        sanitize_path(f"safe/path_{ch}_file.txt")


# ---------------------------------------------------------------------------
# sanitize_path_from_endpoint
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("payload", PATH_TRAVERSAL_PAYLOADS)
def test_sanitize_path_from_endpoint_rejects_traversal(payload):
    with pytest.raises(HTTPException) as excinfo:
        sanitize_path_from_endpoint(payload)
    assert excinfo.value.status_code == 400


def test_sanitize_path_from_endpoint_rejects_absolute():
    with pytest.raises(HTTPException):
        sanitize_path_from_endpoint("/etc/passwd")


def test_sanitize_path_from_endpoint_returns_none_for_none():
    assert sanitize_path_from_endpoint(None) is None


def test_sanitize_path_from_endpoint_normalises_backslashes():
    # Backslashes are folded to forward slashes before pattern checks,
    # so a Windows-style relative path with no traversal is accepted.
    assert sanitize_path_from_endpoint("sub\\dir\\file.txt") == "sub/dir/file.txt"


def test_sanitize_path_from_endpoint_accepts_safe_path():
    assert sanitize_path_from_endpoint("models/foo/bar.bin") == "models/foo/bar.bin"


# ---------------------------------------------------------------------------
# Property: the compiled regex MUST match every short traversal length.
# This is the explicit guard against re-introducing the #641 off-by-one.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("dots", [2, 3, 4, 5, 8, 16])
def test_dot_run_of_any_length_ge_two_is_blocked(dots):
    with pytest.raises(HTTPException):
        sanitize_path("." * dots + "/x")
