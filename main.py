"""
Script for submitting application to B12 via GitHub Actions.
"""

import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any

# import requests


ENDPOINT_URL = "https://b12.io/apply/submission"


def canonicalize_json(payload: dict[str, Any]) -> bytes:
    """
    Convert payload to compact JSON with sorted keys.
    Returns UTF-8 encoded bytes.
    """
    # Sort keys alphabetically and dump with no whitespace
    canonical_json = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    return canonical_json.encode('utf-8')


def calculate_signature(key: str, payload_bytes: bytes) -> str:
    """Calculate HMAC-SHA256 signature."""
    return hmac.new(
        key.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()


def main():
    """Submit application to B12 endpoint."""
    env_var_keys = [
        "SIGNING_SECRET",
        "NAME",
        "EMAIL",
        "RESUME_LINK",
        "REPOSITORY_LINK",
        "ACTION_RUN_LINK",
    ]
    env_vars = {k: os.environ.get(k) for k in env_var_keys}

    missing_env_vars = [k for k, v in env_vars.items() if not v]
    if missing_env_vars:
        print("The following environment variables are required:")
        for var in missing_env_vars:
            print(f"  - {var}")
        sys.exit(1)

    timestamp = datetime.now(timezone.utc).isoformat(
        timespec='milliseconds').replace('+00:00', 'Z')
    payload = {
        "action_run_link": env_vars["ACTION_RUN_LINK"],
        "email": env_vars["EMAIL"],
        "name": env_vars["NAME"],
        "repository_link": env_vars["REPOSITORY_LINK"],
        "resume_link": env_vars["RESUME_LINK"],
        "timestamp": timestamp
    }

    payload_bytes = canonicalize_json(payload)
    signature = calculate_signature(env_vars["SIGNING_SECRET"], payload_bytes)
    print("Payload JSON:", payload_bytes.decode('utf-8'))
    print("Signature:", signature)

    print("Signing secret test:")
    print(env_vars["SIGNING_SECRET"])

    # headers = {
    #     "Content-Type": "application/json",
    #     "X-Signature-256": f"sha256={signature}",
    # }

    # success = False
    # try:
    #     response = requests.post(
    #         ENDPOINT_URL,
    #         data=payload_bytes,
    #         headers=headers,
    #         timeout=10
    #     )

    #     if response.status_code == 200:
    #         result = response.json()

    #         if result.get("success"):
    #             receipt = result.get("receipt", "")
    #             print("Application submitted:")
    #             print(f"Receipt: {receipt}")
    #             success = True
    #         else:
    #             print(f"Submission failed: {result}")
    #     else:
    #         print(f"HTTP Error {response.status_code}: {response.text}")
    # except requests.exceptions.RequestException as e:
    #     print(f"Network error: {e}")
    # except Exception as e:  # pylint: disable=broad-exception-caught
    #     print(f"Unexpected error: {e}")

    # sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
