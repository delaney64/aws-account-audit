# AWS IAM Identity Center (SSO) Access Audit Script

This Python script generates a comprehensive report of user access assignments across AWS accounts managed through AWS IAM Identity Center (formerly AWS SSO). The script exports the data to a CSV file, making it easy to analyze user permissions across your AWS organization.

## Features

- Lists all users from IAM Identity Center
- Maps users to their AWS account assignments
- Includes permission set details for each assignment
- Generates a timestamped CSV report
- Shows account names alongside account IDs
- Handles pagination for large organizations

## Prerequisites

- Python 3.x
- boto3 library (`pip install boto3`)
- AWS credentials configured with appropriate permissions
- Read access to AWS IAM Identity Center
- Read access to AWS Organizations

## Required AWS Permissions

The AWS credentials used must have the following permissions:
- `identitystore:ListUsers`
- `sso-admin:ListInstances`
- `sso-admin:ListPermissionSets`
- `sso-admin:ListAccountAssignments`
- `sso-admin:DescribePermissionSet`
- `organizations:ListAccounts`

## Installation

1. Clone this repository:
```bash
git clone https://github.com/your-username/aws-sso-audit.git
cd aws-sso-audit
```

2. Install required dependencies:
```bash
pip install boto3
```

## Usage

1. Configure your AWS credentials:
```bash
aws configure
```
Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=your_region
```

2. Run the script:
```bash
python aws-sso-audit.py
```

The script will generate a CSV file named `aws_sso_access_report_YYYYMMDD_HHMMSS.csv` in the current directory.

## CSV Output Format

The generated report includes the following columns:
- `UserEmail`: Email address of the user
- `UserName`: Full name of the user
- `AccountId`: AWS account ID
- `AccountName`: AWS account name
- `PermissionSet`: Name of the assigned permission set
- `PrincipalType`: Type of principal (usually "USER")
- `PrincipalId`: Unique identifier of the user

## Error Handling

The script includes error handling for common issues:
- Missing AWS credentials
- Insufficient permissions
- Invalid account IDs
- API throttling

Errors are printed to the console but don't stop the script from completing.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.