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

## SAM / Step Functions / CloudFormation Work

When working with `cerberus/template.yaml`, `cerberus/statemachine/cerberus.asl.json`, or `cft-eventbridge-rule.yaml`, use the `aws-serverless` MCP plugin (https://claude.ai/plugins/aws-serverless). It provides accurate resource schemas, ASL syntax validation, and SAM transform awareness that significantly reduces iteration on these files.

## PR Requirements

CODEOWNERS requires approval from both `@rewindio/AppSec` and `@rewindio/devops` before merging. Do not merge without both approvals.
