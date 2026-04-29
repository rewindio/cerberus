# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Does

Cerberus is an AWS SAM application that automatically removes unwanted default AWS Control Tower IAM Identity Center permission set assignments. It intercepts `CreateAccountAssignment` CloudTrail events and deletes the assignment when it matches configured regex patterns.

## Two-Account Deployment

This app spans two AWS accounts:

- **Management account**: `cft-eventbridge-rule.yaml` is a standalone CloudFormation template (not SAM) that forwards `sso:CreateAccountAssignment` events cross-account to the custom event bus in the delegated admin account.
- **Delegated admin account**: `cerberus/template.yaml` is the SAM app. Deploy here.

Never conflate these two templates. `sam build` / `sam deploy` only touch `cerberus/`.

## Critical Code Quirk

`cerberus/src/cerberus/app.py` around line 120 unconditionally overwrites the real `sso:DeleteAccountAssignment` API response with a hardcoded `{"AccountAssignmentDeletionStatus": {"Status": "SUCCEEDED"}}`. This means the function always reports success regardless of what the API actually returned. Verify intent with the team before modifying this function or adding response-based branching logic.

## Primary Tuning Surface

The three Lambda environment variables below are the main way to control what gets deleted. They are regex patterns set in `cerberus/template.yaml`:

- `PermissionSetNamePattern`
- `PrincipalGroupNamePattern`
- `PrincipalUserNameEmail`

## Testing

Tests use stdlib `unittest`, not pytest. Do not add pytest dependencies or use pytest-style fixtures. Test file: `cerberus/tests/unit/test_cerberus.py`.

## MCP Servers

Two MCP servers are configured in `.mcp.json` at the repo root. Use them proactively — don't guess at AWS API shapes or dig through logs manually.

**`awslabs.aws-documentation-mcp-server`** — AWS official docs, resource schemas, IAM policy references, API signatures. Reach for this whenever you're working on `cerberus/template.yaml`, `cerberus/statemachine/cerberus.asl.json`, or `cft-eventbridge-rule.yaml`, or any time you need to verify an AWS API call, IAM action name, or resource attribute.

The **`aws-serverless` plugin** (`aws-serverless@claude-plugins-official`) is enabled at project scope in `.claude/settings.json`. It provides SAM-aware skills and serverless-specific context on top of the documentation MCP server.

**`awslabs-cloudwatch-mcp-server`** — Live CloudWatch access to the deployed Cerberus stack. Use this to debug Step Functions execution failures, inspect Lambda errors, or trace an event end-to-end. The default log group is `/cerberus` (parameterized at deploy time). The server is pre-configured with `AWS_PROFILE=cerberus` and `AWS_REGION=ca-central-1`; the `cerberus` profile must exist locally with CloudWatch read-only access (see `cerberus/README.md` for profile setup).

## PR Requirements

After opening a PR, run the `code-review` plugin before requesting human review:

```
/code-review
```

The plugin (`code-review@claude-plugins-official`) is enabled at project scope in `.claude/settings.json`. Use it to catch security, logic, and style issues before CODEOWNERS reviewers see the PR.

CODEOWNERS requires approval from both `@rewindio/AppSec` and `@rewindio/devops` before merging. Do not merge without both approvals.
