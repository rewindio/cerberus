# Cerberus

⚠️ This project is currently under development. ⚠️

AWS Control Tower's default behavior in managed mode is to assign baseline [IAM Identity Center Groups for AWS Control Tower](https://docs.aws.amazon.com/en_us/controltower/latest/userguide//sso-groups.html) to newly enrolled accounts. These group assignments are also reapplied when an account update is performed; for instance, when a new version of the landing zone is made available.

The default **IAM Identity Center Groups for AWS Control Tower** are rather permissive. For instance, the `AWSControlTowerAdmins` permission set assigns the `AWSAdministratorAccess` managed IAM policy to the IAM Role. This behavior goes against our policy of maintaining least privilege access to our AWS accounts.

We have created [Cerberus](https://www.britannica.com/topic/Cerberus) to monitor events from the `sso.amazonaws.com` service. Cerberus, often referred to as the hound of Hades, is a multi-headed dog that guards the gates of the underworld to prevent the dead from leaving, or in this case, prevent `CreateAccountAssignment` of unauthorized (unwanted) default permission sets to AWS Control Tower managed accounts.
