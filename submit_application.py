#!/usr/bin/env python3
"""
B12 Application Submission Script
Submits application data to B12 with HMAC-SHA256 signature verification.
"""

import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timezone

import requests


SUBMISSION_URL = "https://b12.io/apply/submission"
SIGNING_SECRET = "hello-there-from-b12"


def create_payload(name, email, resume_link, repository_link, action_run_link):
    """Create the canonicalized JSON payload."""
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
        "name": name,
        "email": email,
        "resume_link": resume_link,
        "repository_link": repository_link,
        "action_run_link": action_run_link,
    }

    # Create compact JSON with sorted keys and no extra whitespace
    return json.dumps(payload, separators=(',', ':'), sort_keys=True, ensure_ascii=False)


def generate_signature(payload_bytes, secret):
    """Generate HMAC-SHA256 signature for the payload."""
    signature = hmac.new(
        secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    )
    return f"sha256={signature.hexdigest()}"


def submit_application(name, email, resume_link, repository_link, action_run_link):
    """Submit the application to B12."""
    # Create payload
    payload_json = create_payload(name, email, resume_link, repository_link, action_run_link)
    payload_bytes = payload_json.encode('utf-8')

    # Generate signature
    signature = generate_signature(payload_bytes, SIGNING_SECRET)

    # Prepare headers
    headers = {
        'Content-Type': 'application/json',
        'X-Signature-256': signature,
    }

    print("Submitting application to B12...")
    print(f"Payload: {payload_json}")
    print(f"Signature: {signature}")

    # Make POST request
    try:
        response = requests.post(
            SUBMISSION_URL,
            data=payload_bytes,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        # Parse and display response
        result = response.json()

        if result.get('success'):
            receipt = result.get('receipt')
            print("\n" + "="*60)
            print("✓ Submission successful!")
            print("="*60)
            print(f"Receipt: {receipt}")
            print("="*60)
            return receipt
        else:
            print(f"Submission failed: {result}")
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"Error submitting application: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        sys.exit(1)


def main():
    """Main entry point."""
    # Get values from environment variables (for GitHub Actions)
    name = os.getenv('APPLICANT_NAME')
    email = os.getenv('APPLICANT_EMAIL')
    resume_link = os.getenv('APPLICANT_RESUME_LINK')
    repository_link = os.getenv('APPLICANT_REPOSITORY_LINK')

    # Construct action_run_link from GitHub Actions environment variables
    github_server = os.getenv('GITHUB_SERVER_URL', 'https://github.com')
    github_repo = os.getenv('GITHUB_REPOSITORY')
    github_run_id = os.getenv('GITHUB_RUN_ID')

    if github_repo and github_run_id:
        action_run_link = f"{github_server}/{github_repo}/actions/runs/{github_run_id}"
    else:
        action_run_link = os.getenv('APPLICANT_ACTION_RUN_LINK')

    # Validate required fields
    missing_fields = []
    if not name:
        missing_fields.append('APPLICANT_NAME')
    if not email:
        missing_fields.append('APPLICANT_EMAIL')
    if not resume_link:
        missing_fields.append('APPLICANT_RESUME_LINK')
    if not repository_link:
        missing_fields.append('APPLICANT_REPOSITORY_LINK')
    if not action_run_link:
        missing_fields.append('APPLICANT_ACTION_RUN_LINK or GITHUB_RUN_ID')

    if missing_fields:
        print("Error: Missing required environment variables:")
        for field in missing_fields:
            print(f"  - {field}")
        print("\nPlease set these environment variables before running the script.")
        sys.exit(1)

    # Submit the application
    submit_application(name, email, resume_link, repository_link, action_run_link)


if __name__ == '__main__':
    main()
