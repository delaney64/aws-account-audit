import boto3
import csv
from datetime import datetime

def get_identity_store_users(identity_store_id):
    """Get all users from Identity Store"""
    identitystore = boto3.client('identitystore')
    users = []
    paginator = identitystore.get_paginator('list_users')
    
    for page in paginator.paginate(IdentityStoreId=identity_store_id):
        users.extend(page['Users'])
    return users

def get_account_assignments(instance_arn, identity_store_id):
    """Get all permission set assignments"""
    sso_admin = boto3.client('sso-admin')
    assignments = []
    
    # Get all permission sets
    paginator = sso_admin.get_paginator('list_permission_sets')
    permission_sets = []
    
    for page in paginator.paginate(InstanceArn=instance_arn):
        permission_sets.extend(page['PermissionSets'])
    
    # Get all AWS accounts
    organizations = boto3.client('organizations')
    try:
        accounts_paginator = organizations.get_paginator('list_accounts')
        accounts = []
        for page in accounts_paginator.paginate():
            accounts.extend(page['Accounts'])
    except Exception as e:
        print(f"Error getting accounts list: {str(e)}")
        accounts = []
    
    # Get assignments for each permission set and account
    for permission_set in permission_sets:
        try:
            # Get permission set name
            ps_response = sso_admin.describe_permission_set(
                InstanceArn=instance_arn,
                PermissionSetArn=permission_set
            )
            ps_name = ps_response['PermissionSet']['Name']
            
            # Check assignments for each account
            for account in accounts:
                try:
                    assign_paginator = sso_admin.get_paginator('list_account_assignments')
                    for page in assign_paginator.paginate(
                        InstanceArn=instance_arn,
                        AccountId=account['Id'],
                        PermissionSetArn=permission_set
                    ):
                        for assignment in page['AccountAssignments']:
                            assignment['PermissionSetName'] = ps_name
                            assignment['AccountName'] = account.get('Name', 'N/A')
                            assignments.append(assignment)
                except Exception as e:
                    print(f"Error checking assignments for account {account['Id']}: {str(e)}")
                    
        except Exception as e:
            print(f"Error processing permission set {permission_set}: {str(e)}")
            
    return assignments

def main():
    # Initialize SSO admin client
    sso_admin = boto3.client('sso-admin')
    
    # Get SSO instance
    instances = sso_admin.list_instances()
    if not instances['Instances']:
        print("No SSO instance found")
        return
    
    instance = instances['Instances'][0]
    instance_arn = instance['InstanceArn']
    identity_store_id = instance['IdentityStoreId']
    
    # Get users and assignments
    print("Fetching users...")
    users = get_identity_store_users(identity_store_id)
    print("Fetching assignments...")
    assignments = get_account_assignments(instance_arn, identity_store_id)
    
    # Prepare CSV output
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'aws_sso_access_report_{timestamp}.csv'
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['UserEmail', 'UserName', 'AccountId', 'AccountName', 'PermissionSet', 'PrincipalType', 'PrincipalId']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Match assignments with users and write to CSV
        for assignment in assignments:
            matching_user = next(
                (user for user in users if user['UserId'] == assignment['PrincipalId']),
                None
            )
            
            if matching_user:
                writer.writerow({
                    'UserEmail': matching_user.get('Emails', [{}])[0].get('Value', 'N/A'),
                    'UserName': f"{matching_user.get('GivenName', '')} {matching_user.get('FamilyName', '')}",
                    'AccountId': assignment['AccountId'],
                    'AccountName': assignment.get('AccountName', 'N/A'),
                    'PermissionSet': assignment['PermissionSetName'],
                    'PrincipalType': assignment['PrincipalType'],
                    'PrincipalId': assignment['PrincipalId']
                })
    
    print(f"Report generated: {filename}")

if __name__ == "__main__":
    main()