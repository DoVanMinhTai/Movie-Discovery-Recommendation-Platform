import glob
import os
import re
import subprocess
from pathlib import Path
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from tests.helpers import (
    parse_env_file, parse_env_keys, parse_env_values,
    parse_docker_compose, get_tracked_python_files, get_tracked_files
)

# Project root — all relative paths resolve from here
ROOT = Path(__file__).resolve().parent.parent

SENSITIVE_VARS = [
    "DB_URL", "DB_URL_PYTHON", "ES_HOST", "ES_URL",
    "CHATBOT_URL", "RECO_URL", "APP_CORS_ALLOWED_ORIGINS", "FRONTEND_PORT"
]

SERVICE_EXPECTED_VARS = {
    "movie-backend": ["DB_URL","DB_USER","DB_PASSWORD","ES_URL","ES_HOST","CHATBOT_URL","RECO_URL","APP_CORS_ALLOWED_ORIGINS","JAVA_OPTS"],
    "movie-chatbot": ["ES_HOST","ES_URL","GROQ_API_KEY","GROQ_MODEL","HF_TOKEN","CHATBOT_PORT"],
    "movie-recommendation": ["DATABASE_URL","ES_HOST","ES_URL","HF_TOKEN","CHATBOT_URL","BACKEND_URL"],
    "movie-frontend": ["VITE_API_BASE_URL"],
}


def get_service_env_keys(service_dict):
    """
    Extract environment variable keys from a docker-compose service dict.
    Handles both list format (["KEY=VALUE", ...]) and dict format ({KEY: VALUE}).
    """
    env = service_dict.get("environment", {})
    if isinstance(env, list):
        keys = []
        for item in env:
            if isinstance(item, str) and "=" in item:
                key, _, _ = item.partition("=")
                keys.append(key.strip())
            elif isinstance(item, str):
                keys.append(item.strip())
        return keys
    elif isinstance(env, dict):
        return list(env.keys())
    return []


# ---------------------------------------------------------------------------
# Property 1 — No Duplicate Keys in Root .env
# ---------------------------------------------------------------------------
# Feature: env-centralization, Property 1: No duplicate keys in root .env
@given(st.just(parse_env_file(str(ROOT / ".env"))))
@settings(max_examples=100)
def test_property1_no_duplicate_keys(env_vars):
    keys = [k for k, _ in env_vars]
    assert len(keys) == len(set(keys)), f"Duplicate keys found: {[k for k in keys if keys.count(k) > 1]}"


# ---------------------------------------------------------------------------
# Property 2 — Dev and Prod Values Differ for Sensitive Variables
# ---------------------------------------------------------------------------
# Feature: env-centralization, Property 2: Dev and prod values differ for sensitive variables
@given(st.sampled_from(SENSITIVE_VARS))
@settings(max_examples=100)
def test_property2_dev_prod_values_differ(var_name):
    prod_path = ROOT / ".env.prod"
    if not prod_path.exists():
        pytest.skip(".env.prod not found — skipping dev/prod diff check")

    dev_dict = dict(parse_env_file(str(ROOT / ".env")))
    prod_dict = dict(parse_env_file(str(prod_path)))

    # Skip if the variable is absent from either file
    assume(var_name in dev_dict and var_name in prod_dict)

    dev_val = dev_dict[var_name]
    prod_val = prod_dict[var_name]
    assert dev_val != prod_val, (
        f"Sensitive variable {var_name!r} has the same value in .env and .env.prod: {dev_val!r}"
    )


# ---------------------------------------------------------------------------
# Property 3 — .env.example Completeness
# ---------------------------------------------------------------------------
# Feature: env-centralization, Property 3: .env.example completeness
@given(st.just(parse_env_keys(str(ROOT / ".env"))))
@settings(max_examples=100)
def test_property3_env_example_completeness(env_keys):
    example_keys = parse_env_keys(str(ROOT / ".env.example"))
    for key in env_keys:
        assert key in example_keys, f"Key {key!r} present in .env but missing from .env.example"


# ---------------------------------------------------------------------------
# Property 4 — No Real Credentials in .env.example
# ---------------------------------------------------------------------------
# Feature: env-centralization, Property 4: No real credentials in .env.example
@given(st.sampled_from(parse_env_values(str(ROOT / ".env.example"))))
@settings(max_examples=100)
def test_property4_no_real_credentials_in_example(value):
    # Skip empty/blank placeholder values
    assume(bool(value))

    # Must not start with known API key prefixes
    assert not value.startswith("hf_"), \
        f"Value looks like a real HuggingFace token: {value!r}"
    assert not value.startswith("gsk_"), \
        f"Value looks like a real Groq API key: {value!r}"

    # Must not contain known production hostnames
    assert "bonsaisearch.net" not in value, \
        f"Value contains a production Bonsai ES hostname: {value!r}"
    assert "supabase.com" not in value, \
        f"Value contains a production Supabase hostname: {value!r}"

    # Must not look like a UUID
    assert not re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-", value), \
        f"Value looks like a UUID: {value!r}"

    # Must not look like a long base64 string (real secret), unless it contains a placeholder marker
    if not ("_here" in value or "YOUR" in value):
        assert not re.search(r"[A-Za-z0-9+/]{20,}={0,2}$", value), \
            f"Value looks like a real base64-encoded secret: {value!r}"


# ---------------------------------------------------------------------------
# Property 5 — Per-Service .env.example Coverage
# ---------------------------------------------------------------------------
# Feature: env-centralization, Property 5: Per-service .env.example coverage
@given(st.sampled_from(list(SERVICE_EXPECTED_VARS.items())))
@settings(max_examples=100)
def test_property5_per_service_env_example_coverage(service_and_vars):
    service, expected_vars = service_and_vars
    example_path = ROOT / service / ".env.example"
    assert example_path.exists(), f"{service}/.env.example does not exist"

    actual_keys = parse_env_keys(str(example_path))
    for var in expected_vars:
        assert var in actual_keys, (
            f"Variable {var!r} expected in {service}/.env.example but not found. "
            f"Present keys: {actual_keys}"
        )


# ---------------------------------------------------------------------------
# Property 6 — No Auto-Loading in Python Services
# ---------------------------------------------------------------------------
# Feature: env-centralization, Property 6: No auto-loading in Python services
@given(st.just(None))  # sampled_from requires non-empty; we resolve the list lazily below
@settings(max_examples=1)  # gate: just checks list is non-empty, actual sampling done inside
def _test_property6_gate(dummy):
    pass  # placeholder — see real test below


# Collect files at module level so @given can use sampled_from
_py_files = get_tracked_python_files(["movie-chatbot", "movie-recommendation"])
# Exclude scripts/ directories - those are standalone utilities that may need load_dotenv
_py_files = [f for f in _py_files if "scripts" not in Path(f).parts and "__pycache__" not in Path(f).parts]


@pytest.mark.skipif(not _py_files, reason="No tracked Python files found in chatbot/recommendation services")
@given(st.sampled_from(_py_files))
@settings(max_examples=100)
def test_property6_no_auto_loading_in_python_services(filepath):
    content = Path(filepath).read_text(encoding="utf-8", errors="replace")
    assert "load_dotenv()" not in content, \
        f"Found unconditional load_dotenv() call in {filepath}"
    assert 'env_file=".env"' not in content, \
        f"Found env_file=\".env\" in SettingsConfigDict in {filepath}"


# ---------------------------------------------------------------------------
# Property 7 — .env.example Files Are Never Git-Ignored
# ---------------------------------------------------------------------------
# Feature: env-centralization, Property 7: .env.example files are never git-ignored
_env_examples = glob.glob(str(ROOT / "**" / ".env.example"), recursive=True)


@pytest.mark.skipif(not _env_examples, reason="No .env.example files found in repository")
@given(st.sampled_from(_env_examples))
@settings(max_examples=100)
def test_property7_env_examples_not_git_ignored(filepath):
    result = subprocess.run(
        ["git", "check-ignore", "--quiet", filepath],
        cwd=str(ROOT),
        capture_output=True,
    )
    assert result.returncode != 0, (
        f"{filepath} is git-ignored — .env.example files must always be trackable"
    )


# ---------------------------------------------------------------------------
# Property 8 — No Real .env Files Are Git-Tracked
# ---------------------------------------------------------------------------
# Feature: env-centralization, Property 8: No real .env files are git-tracked
@given(st.just(None))
@settings(max_examples=100)
def test_property8_no_real_env_files_git_tracked(dummy):
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "git ls-files failed"

    tracked_files = result.stdout.splitlines()
    # Pattern matches .env, .env.local, .env.production, .env.prod at any directory depth
    env_pattern = re.compile(r"(^|/)\.env(\.(local|production|prod))?$")
    offending = [f for f in tracked_files if env_pattern.search(f)]
    assert not offending, (
        f"Real .env files are git-tracked (must be in .gitignore): {offending}"
    )


# ---------------------------------------------------------------------------
# Property 9 — Consistent ES_HOST Across All Docker Compose Services
# ---------------------------------------------------------------------------
# Feature: env-centralization, Property 9: Consistent ES_HOST across all docker-compose services
@given(st.just(parse_docker_compose(str(ROOT / "docker-compose.yml"))))
@settings(max_examples=100)
def test_property9_consistent_es_host_in_docker_compose(compose_config):
    services = compose_config.get("services", {})
    es_services = ["movie-backend", "chatbot", "recommendation", "initializer", "mage"]

    for svc_name in es_services:
        assert svc_name in services, f"Service {svc_name!r} not found in docker-compose.yml"
        svc = services[svc_name]
        env = svc.get("environment", {})

        # Resolve ES_HOST value regardless of list or dict format
        es_host_value = None
        if isinstance(env, list):
            for item in env:
                if isinstance(item, str) and item.startswith("ES_HOST="):
                    _, _, es_host_value = item.partition("=")
                    break
        elif isinstance(env, dict):
            es_host_value = env.get("ES_HOST")

        assert es_host_value is not None, \
            f"ES_HOST not found in {svc_name!r} environment block"
        assert "${ES_HOST}" in es_host_value or es_host_value == "${ES_HOST}", (
            f"ES_HOST in service {svc_name!r} is hardcoded ({es_host_value!r}) "
            f"instead of referencing ${{ES_HOST}}"
        )


# ---------------------------------------------------------------------------
# Property 10 — No Hardcoded Bonsai URLs in Chatbot Source
# ---------------------------------------------------------------------------
# Feature: env-centralization, Property 10: No hardcoded Bonsai URLs in chatbot source
_chatbot_tracked = get_tracked_files("movie-chatbot")


@pytest.mark.skipif(not _chatbot_tracked, reason="No tracked files found in movie-chatbot")
@given(st.sampled_from(_chatbot_tracked))
@settings(max_examples=100)
def test_property10_no_hardcoded_bonsai_urls_in_chatbot(filepath):
    try:
        content = Path(filepath).read_text(encoding="utf-8")
    except (UnicodeDecodeError, IsADirectoryError):
        # Skip binary files or directories
        return

    assert "bonsaisearch.net" not in content, (
        f"Hardcoded Bonsai URL found in {filepath} — must use injected ES_HOST env var"
    )


# ---------------------------------------------------------------------------
# Property 11 — Chatbot and Recommendation Services Receive Only Required Variables
# ---------------------------------------------------------------------------
# Feature: env-centralization, Property 11: Chatbot and recommendation services receive only required variables
@given(st.just(parse_docker_compose(str(ROOT / "docker-compose.yml"))))
@settings(max_examples=100)
def test_property11_services_receive_only_required_variables(compose_config):
    services = compose_config.get("services", {})

    allowed_chatbot_keys = {
        "PYTHONUNBUFFERED", "ES_HOST", "ES_URL",
        "GROQ_API_KEY", "GROQ_MODEL", "HF_TOKEN"
    }
    allowed_recommendation_keys = {
        "DATABASE_URL", "ES_HOST", "ES_URL",
        "HF_TOKEN", "CHATBOT_URL", "BACKEND_URL"
    }

    assert "chatbot" in services, "Service 'chatbot' not found in docker-compose.yml"
    assert "recommendation" in services, "Service 'recommendation' not found in docker-compose.yml"

    chatbot_keys = set(get_service_env_keys(services["chatbot"]))
    recommendation_keys = set(get_service_env_keys(services["recommendation"]))

    extra_chatbot = chatbot_keys - allowed_chatbot_keys
    assert not extra_chatbot, (
        f"chatbot service has unexpected env vars: {extra_chatbot}. "
        f"Allowed: {allowed_chatbot_keys}"
    )

    extra_recommendation = recommendation_keys - allowed_recommendation_keys
    assert not extra_recommendation, (
        f"recommendation service has unexpected env vars: {extra_recommendation}. "
        f"Allowed: {allowed_recommendation_keys}"
    )
