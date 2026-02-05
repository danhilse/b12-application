# B12 Application Submission

This repository contains a Python script to submit an application to B12 via their API endpoint, with HMAC-SHA256 signature verification.

## Files

- `submit_application.py` - Python script that submits the application
- `.github/workflows/submit-application.yml` - GitHub Actions workflow
- `requirements.txt` - Python dependencies

## Setup

### 1. Configure GitHub Secrets

Go to your repository's Settings → Secrets and variables → Actions, and add the following secrets:

- `APPLICANT_NAME` - Your full name
- `APPLICANT_EMAIL` - Your email address
- `APPLICANT_RESUME_LINK` - URL to your resume (PDF, HTML, or LinkedIn profile)
- `APPLICANT_REPOSITORY_LINK` - URL to this repository (e.g., `https://github.com/yourusername/yourrepo`)

### 2. Run the Workflow

#### Option A: Manual Trigger
1. Go to the Actions tab in your GitHub repository
2. Select "Submit B12 Application" workflow
3. Click "Run workflow"
4. The workflow will execute and display the receipt in the logs

#### Option B: Automatic on Push
The workflow is configured to run automatically when you push to the `main` branch.

### 3. Retrieve Your Receipt

After the workflow completes:
1. Go to the Actions tab
2. Click on the latest workflow run
3. Open the "Submit application to B12" step
4. Copy the receipt from the output

The receipt will be displayed like this:
```
============================================================
✓ Submission successful!
============================================================
Receipt: your-submission-receipt
============================================================
```

## Local Testing

You can also run the script locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export APPLICANT_NAME="Your Name"
export APPLICANT_EMAIL="you@example.com"
export APPLICANT_RESUME_LINK="https://your-resume-url.com"
export APPLICANT_REPOSITORY_LINK="https://github.com/yourusername/yourrepo"
export APPLICANT_ACTION_RUN_LINK="https://github.com/yourusername/yourrepo/actions/runs/123456"

# Run the script
python submit_application.py
```

## How It Works

The script:
1. Creates an ISO 8601 timestamp
2. Constructs a JSON payload with all required fields
3. Canonicalizes the JSON (sorted keys, compact format, UTF-8 encoded)
4. Generates an HMAC-SHA256 signature using the signing secret
5. POSTs to `https://b12.io/apply/submission` with the `X-Signature-256` header
6. Displays the receipt upon success

## Signature Verification Example

For the payload:
```json
{"action_run_link":"https://link-to-github-or-another-forge.example.com/your/repository/actions/runs/run_id","email":"you@example.com","name":"Your name","repository_link":"https://link-to-github-or-other-forge.example.com/your/repository","resume_link":"https://pdf-or-html-or-linkedin.example.com","timestamp":"2026-01-06T16:59:37.571Z"}
```

The HMAC-SHA256 signature with secret `hello-there-from-b12` produces:
```
sha256=c5db257a56e3c258ec1162459c9a295280871269f4cf70146d2c9f1b52671d45
```

## Other CI/CD Platforms

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
submit_application:
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - python submit_application.py
  variables:
    APPLICANT_NAME: $APPLICANT_NAME
    APPLICANT_EMAIL: $APPLICANT_EMAIL
    APPLICANT_RESUME_LINK: $APPLICANT_RESUME_LINK
    APPLICANT_REPOSITORY_LINK: $APPLICANT_REPOSITORY_LINK
    APPLICANT_ACTION_RUN_LINK: $CI_PIPELINE_URL
  only:
    - main
```

Set the variables in GitLab's CI/CD settings.

### CircleCI

Create `.circleci/config.yml`:

```yaml
version: 2.1

jobs:
  submit:
    docker:
      - image: python:3.11
    steps:
      - checkout
      - run:
          name: Install dependencies
          command: pip install -r requirements.txt
      - run:
          name: Submit application
          command: python submit_application.py

workflows:
  submit_application:
    jobs:
      - submit:
          context: b12-application
```

Set environment variables in CircleCI's project settings.
