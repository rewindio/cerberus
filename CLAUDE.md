# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Does

Cerberus is an AWS SAM application that automatically removes unwanted default AWS Control Tower IAM Identity Center permission set assignments. It intercepts `CreateAccountAssignment` CloudTrail events and deletes the assignment when it matches configured regex patterns.

## Single-Account Deployment in the Management Account

Cerberus must be deployed in the AWS Organization management account. IAM Identity Center enforces a service-level restriction (invisible to IAM, SCPs, and the delegated-admin configuration): permission sets whose lifecycle is owned by the management account — every Control Tower default — can only have their assignments removed by a principal in the management account itself. A delegated admin returns `AccessDeniedException` regardless of IAM permissions, which is why Cerberus does not run in a delegated-admin account.

`cerberus/template.yaml` is the SAM app. Deploy it in the management account. There are no other CloudFormation templates in the repository.

## Primary Tuning Surface

Lambda environment variables (set in `cerberus/template.yaml`):

- `PermissionSetNamePattern` — regex matched against the permission set name (case-insensitive).
- `PrincipalGroupNamePattern` — regex matched against the principal name when `principalType=GROUP`.
- `PrincipalUserNameEmail` — exact email match against the principal name when `principalType=USER`.
- `Mode` — `ENFORCE` | `DRY_RUN` | `DISABLED`. `DRY_RUN` logs would-delete decisions without calling the SSO API; `DISABLED` turns off the EventBridge rule and short-circuits the Lambda. Operational kill switch + dry-run capability.

## Testing

Tests use stdlib `unittest`, not pytest. Do not add pytest dependencies or use pytest-style fixtures. Test file: `cerberus/tests/unit/test_cerberus.py`.

## MCP Servers

Two MCP servers are configured in `.mcp.json` at the repo root. Use them proactively — don't guess at AWS API shapes or dig through logs manually.

**`awslabs.aws-documentation-mcp-server`** — AWS official docs, resource schemas, IAM policy references, API signatures. Reach for this whenever you're working on `cerberus/template.yaml` or `cerberus/statemachine/cerberus.asl.json`, or any time you need to verify an AWS API call, IAM action name, or resource attribute.

**`awslabs-cloudwatch-mcp-server`** — Live CloudWatch access to the deployed Cerberus stack. Use this to debug Step Functions execution failures, inspect Lambda errors, or trace an event end-to-end. The default log group is `/cerberus` (parameterized at deploy time). The server is pre-configured with `AWS_PROFILE=cerberus` and `AWS_REGION=ca-central-1`; the `cerberus` profile must exist locally with CloudWatch read-only access (see `cerberus/README.md` for profile setup).

## Plugins

The **`aws-serverless` plugin** (`aws-serverless@claude-plugins-official`) is enabled at project scope in `.claude/settings.json`. It provides SAM-aware skills and serverless-specific context for working with `cerberus/template.yaml` and `cerberus/statemachine/cerberus.asl.json`.

The **`code-review` plugin** (`code-review@claude-plugins-official`) is also enabled. See PR Requirements below.

## PR Requirements

After opening a PR:

1. Run `/code-review` and read the full output before doing anything else
2. Address any issues identified — push fixes to the branch if needed
3. Post the complete `/code-review` output as a PR comment via `gh pr comment <number> --body "..."` so human reviewers have the analysis in context
4. Only then request human review from CODEOWNERS

CODEOWNERS requires approval from both `@rewindio/AppSec` and `@rewindio/devops` before merging. Do not merge without both approvals.
