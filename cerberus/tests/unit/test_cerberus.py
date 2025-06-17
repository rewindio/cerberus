import unittest
from unittest.mock import patch, MagicMock
from cerberus.src.cerberus.app import lambda_handler
import os


class TestLambdaHandler(unittest.TestCase):

    @patch("cerberus.src.cerberus.app.logger")
    @patch("cerberus.src.cerberus.app.client", new_callable=MagicMock)
    def test_lambda_handler_successful_deletion(self, mock_client, mock_logger):
        event = {
            "DescribeInstance": {
                "InstanceArn": "arn:aws:sso:::instance/sso-instance-id"
            },
            "RequestParameters": {
                "targetId": "target-id",
                "targetType": "AWS_ACCOUNT",
                "principalType": "USER",
                "principalId": "user-id",
            },
            "DescribePermissionSet": {
                "PermissionSet": {
                    "PermissionSetArn": "arn:aws:sso:::permissionSet/sso-instance-id/permission-set-id",
                    "Name": "MatchingPermissionSetName",
                }
            },
            "DescribeUser": {"UserName": "matchinguser@example.com"},
        }
        os.environ["PermissionSetNamePattern"] = "^MatchingPermissionSetName$"
        os.environ["PrincipalGroupNamePattern"] = "^MatchingGroupName$"
        os.environ["PrincipalUserNameEmail"] = "matchinguser@example.com"
        mock_client.delete_account_assignment.return_value = {
            "AccountAssignmentDeletionStatus": {"Status": "SUCCEEDED"}
        }
        result = lambda_handler(event, None)
        self.assertEqual(result["result"], "SUCCESS")
        self.assertIn("Account assignment deletion succeeded", result["message"])

    @patch("cerberus.src.cerberus.app.logger")
    @patch("cerberus.src.cerberus.app.client", new_callable=MagicMock)
    def test_lambda_handler_no_action_taken(self, mock_client, mock_logger):
        event = {
            "DescribeInstance": {
                "InstanceArn": "arn:aws:sso:::instance/sso-instance-id"
            },
            "RequestParameters": {
                "targetId": "target-id",
                "targetType": "AWS_ACCOUNT",
                "principalType": "USER",
                "principalId": "user-id",
            },
            "DescribePermissionSet": {
                "PermissionSet": {
                    "PermissionSetArn": "arn:aws:sso:::permissionSet/sso-instance-id/permission-set-id",
                    "Name": "NonMatchingPermissionSet",
                }
            },
            "DescribeUser": {"UserName": "nonmatchinguser@example.com"},
        }
        os.environ["PermissionSetNamePattern"] = "^MatchingPermissionSetName$"
        os.environ["PrincipalGroupNamePattern"] = "^MatchingGroupName$"
        os.environ["PrincipalUserNameEmail"] = "matchinguser@example.com"
        mock_client.delete_account_assignment.return_value = {
            "AccountAssignmentDeletionStatus": {"Status": "SUCCEEDED"}
        }
        result = lambda_handler(event, None)
        self.assertEqual(result["result"], "SUCCESS")
        self.assertIn("No action taken for principal", result["message"])

    @patch("cerberus.src.cerberus.app.logger")
    @patch("cerberus.src.cerberus.app.client", new_callable=MagicMock)
    def test_lambda_handler_regex_pattern_error(self, mock_client, mock_logger):
        event = {
            "DescribeInstance": {
                "InstanceArn": "arn:aws:sso:::instance/sso-instance-id"
            },
            "RequestParameters": {
                "targetId": "target-id",
                "targetType": "AWS_ACCOUNT",
                "principalType": "USER",
                "principalId": "user-id",
            },
            "DescribePermissionSet": {
                "PermissionSet": {
                    "PermissionSetArn": "arn:aws:sso:::permissionSet/sso-instance-id/permission-set-id",
                    "Name": "MatchingPermissionSetName",
                }
            },
            "DescribeUser": {"UserName": "matchinguser@example.com"},
        }
        os.environ["PermissionSetNamePattern"] = "["
        os.environ["PrincipalGroupNamePattern"] = "^MatchingGroupName$"
        os.environ["PrincipalUserNameEmail"] = "matchinguser@example.com"
        mock_client.delete_account_assignment.return_value = {
            "AccountAssignmentDeletionStatus": {"Status": "SUCCEEDED"}
        }
        result = lambda_handler(event, None)
        self.assertEqual(result["result"], "FAILED")
        self.assertIn("Invalid regex pattern", result["message"])
