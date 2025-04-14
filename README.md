# IAM Metadata Sync

This project collects IAM user metadata from one or multiple AWS accounts (within an AWS Organization) and stores the results in a MySQL database (hosted on AWS RDS).

## 📦 Features

- Fetch IAM users from multiple AWS accounts using STS assume-role
- Collect:
  - User name, ARN, creation date
  - Console access status
  - Access keys with age and last used
  - Signing certificates
  - User-defined tags
- Store data in MySQL (RDS)
- Ready for automation and reporting

---

## ⚙️ Requirements

- Python 3.7+
- AWS credentials configured with permissions to `sts:AssumeRole`
- MySQL database (RDS) provisioned and reachable

---

## 🚀 How to Use

### 1. Install dependencies

```bash
pip install -r requirements.txt

---

# 🔐 Required IAM Permissions

To collect IAM metadata from multiple AWS accounts, you must create a role in each child account (e.g., `IAMMetadataReadRole`) that your main account can assume.

This document outlines the necessary **trust policy** and **permissions policy** for cross-account access.

---

## ✅ Trust Policy

This policy allows the **main account** to assume the role in a **child account**.

Replace `<your-main-account-id>` with your actual AWS Account ID.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<your-main-account-id>:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
