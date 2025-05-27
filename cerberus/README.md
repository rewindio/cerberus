# Cerberus

Cerberus is a [AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-getting-started.html) serverless application for managing AWS resources with the SAM CLI.

AWS SAM Amazon States Language (ASL) diagram of the Cerberus state machine.

![Cerberus SAM ASL](../static/stepfunctions_graph.png)

## Build and Deploy

### Build

Use the following command to build the application:

```bash
sam build --use-container
```

### Deploy

Deploy the application with the following command:

```bash
sam deploy --region us-east-1 --parameter-overrides ManagementAccountId=012345678901 LogGroupName=/cerberus
```

To include RegEx patterns for permissions and principals, use:

```bash
sam deploy --region us-east-1 --parameter-overrides ManagementAccountId=012345678901 LogGroupName=/cerberus PermissionSetNamePattern='^AWS(?:OrganizationsFullAccess|ReadOnlyAccess|ServiceCatalogEndUserAccess|ServiceCatalogAdminFullAccess|PowerUserAccess|AdministratorAccess)$' PrincipalNamePattern='^AWS(?:LogArchiveViewers|LogArchiveAdmins|ControlTowerAdmins|AccountFactory|AuditAccountAdmins|SecurityAuditors|ServiceCatalogAdmins|SecurityAuditPowerUsers)$'
```

## Testing

### Unit Tests

Run unit tests using the following commands:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r tests/requirements.txt
python3 -m unittest discover -v
```

## Cleanup

To delete the deployed stack, use:

```bash
sam delete --stack-name "cerberus"
```
