import boto3
import mysql.connector
import json
from datetime import datetime, timezone
from config import DB_CONFIG

# List of accounts and role names
ACCOUNTS = [
    {'account_id': '411097807674', 'role': 'IAMMetadataReadRole'}
    # Add more accounts here if needed
]

def assume_role(account_id, role_name):
    sts = boto3.client('sts')
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"

    response = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName="IAMCrossAccountSession"
    )

    creds = response['Credentials']

    return boto3.client(
        'iam',
        aws_access_key_id=creds['AccessKeyId'],
        aws_secret_access_key=creds['SecretAccessKey'],
        aws_session_token=creds['SessionToken']
    )

def days_between_dates(date):
    today = datetime.now(timezone.utc)
    return (today - date).days

def get_full_user_metadata(user_name, iam):
    info = {'user_name': user_name}

    user = iam.get_user(UserName=user_name)['User']
    info['arn'] = user['Arn']
    info['create_date'] = user['CreateDate']
    try:
        iam.get_login_profile(UserName=user_name)
        info['console_access'] = 'Enabled'
    except iam.exceptions.NoSuchEntityException:
        info['console_access'] = 'Disabled'

    keys = iam.list_access_keys(UserName=user_name)['AccessKeyMetadata']
    access_keys_info = []
    for key in keys:
        access_key_id = key['AccessKeyId']
        key_status = key['Status']
        created = key['CreateDate']
        age = days_between_dates(created)

        last_used_resp = iam.get_access_key_last_used(AccessKeyId=access_key_id)
        last_used = last_used_resp.get('AccessKeyLastUsed', {}).get('LastUsedDate')

        access_keys_info.append({
            'AccessKeyId': access_key_id,
            'Status': key_status,
            'KeyAgeDays': age,
            'LastUsed': last_used.isoformat() if last_used else None
        })

    info['access_keys'] = access_keys_info

    certs = iam.list_signing_certificates(UserName=user_name)['Certificates']
    info['signing_certs'] = [cert['CertificateId'] for cert in certs]

    tags = iam.list_user_tags(UserName=user_name)['Tags']
    info['tags'] = {tag['Key']: tag['Value'] for tag in tags}

    return info

def save_user_to_mysql(data, account_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Use account ID as prefix for user_name (as primary key)
    user_pk = f"{account_id}:{data['user_name']}"

    cursor.execute("""
        REPLACE INTO iam_user_metadata (
            user_name, arn, create_date, console_access, access_keys, signing_certs, tags
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        user_pk,
        data['arn'],
        data['create_date'],
        data['console_access'],
        json.dumps(data['access_keys']),
        json.dumps(data['signing_certs']),
        json.dumps(data['tags'])
    ))

    conn.commit()
    cursor.close()
    conn.close()

def main():
    for acc in ACCOUNTS:
        account_id = acc['account_id']
        role_name = acc['role']
        print(f"\nAccessing account {account_id}...")

        iam = assume_role(account_id, role_name)
        users = iam.list_users()['Users']

        for user in users:
            user_name = user['UserName']
            print(f"Collecting metadata for: {user_name}")
            data = get_full_user_metadata(user_name, iam)
            save_user_to_mysql(data, account_id)
            print(f"Saved: {account_id}:{user_name}")

if __name__ == "__main__":
    main()
