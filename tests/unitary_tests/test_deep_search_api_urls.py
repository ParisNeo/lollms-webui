"""
Tests for the deep_search function's Google and Bing settings: the default
addresses stay the public APIs, and the static parameters override them.
"""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

FUNCTION_PATH = (
    Path(__file__).resolve().parents[2]
    / "zoos" / "functions_zoo" / "data_search" / "deep_search" / "function.py"
)


@pytest.fixture
def deep_search_module():
    spec = importlib.util.spec_from_file_location("deep_search_function", FUNCTION_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def deep_search(deep_search_module, tmp_path):
    app = SimpleNamespace(
        personality=None,
        lollms_paths=SimpleNamespace(
            personal_configuration_path=tmp_path / "configs",
            personal_outputs_path=tmp_path / "outputs",
        ),
    )
    fn = deep_search_module.DeepSearch(app, client=None)
    fn.api_keys = {"google": "test-key", "bing": "test-key", "serp": ""}
    fn._extract_content_from_url = lambda url, timeout: ""
    return fn


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def capture_get(monkeypatch, module, payload):
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return FakeResponse(payload)

    monkeypatch.setattr(module.requests, "get", fake_get)
    return calls


def test_google_defaults_to_public_api(deep_search, deep_search_module, monkeypatch):
    calls = capture_get(monkeypatch, deep_search_module, {"items": [{"title": "t", "link": "https://a.example"}]})
    deep_search.static_parameters.google_cx = "engine-id"

    results = deep_search._search_google("query", 3, 5)

    assert calls[0][0] == "https://www.googleapis.com/customsearch/v1"
    assert calls[0][1]["params"]["cx"] == "engine-id"
    assert results[0]["url"] == "https://a.example"


def test_google_uses_configured_url(deep_search, deep_search_module, monkeypatch):
    calls = capture_get(monkeypatch, deep_search_module, {"items": []})
    deep_search.static_parameters.google_cx = "engine-id"
    deep_search.static_parameters.google_api_url = "http://localhost:8080/customsearch/v1"

    deep_search._search_google("query", 3, 5)

    assert calls[0][0] == "http://localhost:8080/customsearch/v1"


def test_google_without_cx_makes_no_request(deep_search, deep_search_module, monkeypatch):
    calls = capture_get(monkeypatch, deep_search_module, {"items": []})

    assert deep_search._search_google("query", 3, 5) == []
    assert calls == []


def test_bing_defaults_to_public_api(deep_search, deep_search_module, monkeypatch):
    calls = capture_get(monkeypatch, deep_search_module, {"webPages": {"value": [{"name": "n", "url": "https://b.example"}]}})

    results = deep_search._search_bing("query", 3, 5)

    assert calls[0][0] == "https://api.bing.microsoft.com/v7.0/search"
    assert results[0]["url"] == "https://b.example"


def test_bing_uses_configured_url(deep_search, deep_search_module, monkeypatch):
    calls = capture_get(monkeypatch, deep_search_module, {"webPages": {"value": []}})
    deep_search.static_parameters.bing_api_url = "http://localhost:8080/v7.0/search"

    deep_search._search_bing("query", 3, 5)

    assert calls[0][0] == "http://localhost:8080/v7.0/search"
