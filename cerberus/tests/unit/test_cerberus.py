import unittest
from unittest.mock import patch
from cerberus.src.cerberus.app import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch("cerberus.src.cerberus.app.logger")
    def test_lambda_handler_successful_deletion(self, mock_logger):
        event = {
            "DescribeInstance": {"InstanceArn": "arn:aws:sso:::instance/some-instance"},
            "RequestParameters": {
                "targetId": "123456789012",
                "targetType": "AWS_ACCOUNT",
                "principalType": "USER",
                "principalId": "some-id",
            },
            "DescribePermissionSet": {
                "PermissionSet": {
                    "PermissionSetArn": "arn:aws:sso:::permissionSet/some-permission-set",
                    "Name": "SomePermissionSet",
                }
            },
            "DescribeUser": {"DisplayName": "SomeUser"},
        }
        with patch(
            "cerberus.src.cerberus.app.os.environ",
            {
                "PermissionSetNamePattern": ".*",
                "PrincipalUserNameEmail": ".*",
                "PrincipalGroupNamePattern": ".*",
            },
        ), patch(
            "cerberus.src.cerberus.app.client.delete_account_assignment",
            return_value={"AccountAssignmentDeletionStatus": {"Status": "SUCCEEDED"}},
        ):
            result = lambda_handler(event, None)
        self.assertEqual(result["result"], "SUCCESS")
        self.assertIn("Account assignment deletion succeeded", result["message"])

    @patch("cerberus.src.cerberus.app.logger")
    def test_lambda_handler_no_action_taken(self, mock_logger):
        event = {
            "DescribeInstance": {"InstanceArn": "arn:aws:sso:::instance/some-instance"},
            "RequestParameters": {
                "targetId": "123456789012",
                "targetType": "AWS_ACCOUNT",
                "principalType": "USER",
                "principalId": "some-id",
            },
            "DescribePermissionSet": {
                "PermissionSet": {
                    "PermissionSetArn": "arn:aws:sso:::permissionSet/some-permission-set",
                    "Name": "NonMatchingPermissionSet",
                }
            },
            "DescribeUser": {"DisplayName": "NonMatchingUser"},
        }
        with patch(
            "cerberus.src.cerberus.app.os.environ",
            {
                "PermissionSetNamePattern": "MatchingPattern",
                "PrincipalUserNamePattern": "MatchingPattern",
                "PrincipalGroupNamePattern": "MatchingPattern",
            },
        ):
            result = lambda_handler(event, None)
        self.assertEqual(result["result"], "SUCCESS")
        self.assertIn("No action taken for principal", result["message"])

    @patch("cerberus.src.cerberus.app.logger")
    def test_lambda_handler_regex_pattern_error(self, mock_logger):
        event = {
            "DescribeInstance": {"InstanceArn": "arn:aws:sso:::instance/some-instance"},
            "RequestParameters": {
                "targetId": "123456789012",
                "targetType": "AWS_ACCOUNT",
                "principalType": "USER",
                "principalId": "some-id",
            },
            "DescribePermissionSet": {
                "PermissionSet": {
                    "PermissionSetArn": "arn:aws:sso:::permissionSet/some-permission-set",
                    "Name": "SomePermissionSet",
                }
            },
            "DescribeUser": {"DisplayName": "SomeUser"},
        }
        with patch(
            "cerberus.src.cerberus.app.os.environ",
            {
                "PermissionSetNamePattern": "[",
                "PrincipalUserNamePattern": ".*",
                "PrincipalGroupNamePattern": ".*",
            },
        ):
            result = lambda_handler(event, None)
        self.assertEqual(result["result"], "FAILED")
        self.assertIn("Invalid regex pattern", result["message"])
