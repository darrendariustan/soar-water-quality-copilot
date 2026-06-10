# Part 12A: AWS Configurations & Setup Required

This document provides step-by-step instructions to configure the necessary AWS infrastructure in your AWS Console before proceeding with the deployment of the WaterForAll application.

## 1. Amazon RDS for PostgreSQL (with pgvector) - DONE

We need a database to store knowledge, test results, and perform semantic searches using `pgvector`.

**Steps:**
1. Navigate to the **RDS** console.
2. Click the **Create database** dropdown and choose **Full configuration** (this replaces the old "Standard create" option).
3. Select **PostgreSQL** and choose engine version **18.3-R1** (or latest available).
4. Under **Templates**, select **Free tier** (if available and sufficient) or **Dev/Test**.
5. Under **Availability and durability**, select **Single-AZ DB instance deployment (1 instance)** to minimize costs for this deployment.
6. **Settings**: 
   - Set the **DB instance identifier** (e.g., `waterforall-db`).
   - Set the **Master username** (e.g., `postgres`).
   - Auto-generate a password or create your own, and save it securely.
7. **Instance configuration**: Choose the **Burstable classes (includes t classes)** radio button, then select an instance type like `db.t3.micro` or `db.t4g.micro`.
8. **Storage**: Leave as **General Purpose SSD (gp3)**, but lower **Allocated storage** to **20 GiB** to save costs.
9. **Connectivity**: 
   - Choose **Don't connect to an EC2 compute resource**.
   - Ensure it's in the default VPC or your chosen VPC.
   - Set **Public access** to **No** (best practice) or **Yes** if you need to connect directly from your local machine during development.
   - For **VPC security group**, select **Create new** (recommended) and enter a name like `waterforall-rds-sg`. This ensures AWS automatically creates a firewall rule allowing traffic on PostgreSQL's default port (5432).
10. **Monitoring**: Uncheck **Enable Performance Insights** and **Enable Enhanced monitoring** to save costs. Leave other fields default.
11. **Additional configuration**:
    - **Initial database name**: Leave empty (RDS creates a default `postgres` database automatically).
    - **Enable automated backup**: Uncheck to save storage costs for the MVP.
    - **Enable encryption**: Leave checked.
    - **Enable auto minor version upgrade**: Leave checked.
    - **Enable deletion protection**: Leave unchecked.
12. Click **Create database**.
13. *Note the database endpoint URL once it becomes available. You will need it to construct your `DATABASE_URL`.*

## 2. Amazon S3 (Simple Storage Service) - DONE

S3 will store raw crawled documents, test kit photos, and source snapshots.

**Steps:**
1. Navigate to the **S3** console.
2. Click **Create bucket**.
3. **Bucket name**: Enter a globally unique name (e.g., `waterforall-dev-cv-images` or similar).
4. **Region**: Choose the same region as your RDS instance.
5. **Object Ownership**: ACLs disabled (recommended).
6. **Block Public Access**: Check "Block all public access" (you can generate pre-signed URLs from the backend for image uploads).
7. Click **Create bucket**.
8. **Note**: The bucket will be empty initially. Your FastAPI backend will programmatically upload user photos and crawled documents here during runtime. Copy your newly created bucket name and add it to your `.env` file as `AWS_S3_BUCKET=waterforall-dev-cv-images`.

## 3. Amazon Elastic Container Registry (ECR) - DONE

We need a repository to hold the FastAPI backend and LangGraph agents Docker image. 

*Note: You already have an existing repository named `waterforall-cv` containing your images. You can reuse this repository, so you do not need to recreate it.*

**Steps (if creating a new one):**
1. Navigate to the **Elastic Container Registry (ECR)** console.
2. Under Private registry, click **Repositories** and then **Create repository**.
3. **Visibility settings**: Private.
4. **Repository name**: `waterforall-backend` (or use your existing `waterforall-cv`).
5. Click **Create repository**.
6. *Click into the newly created repository and click "View push commands" to see how to authenticate and push your local Docker image later.*

## 4. AWS Secrets Manager - DONE

Securely store API keys and database connection strings instead of hardcoding them.

**Steps:**
1. Navigate to **Secrets Manager**.
2. Click **Store a new secret**.
3. **Secret type**: Choose **Other type of secret**.
4. Create Key/Value pairs for the following (matching your `.env`):
   - `OPENAI_API_KEY`: [Your OpenAI Key]
   - `EXA_API_KEY`: [Your Exa Key]
   - `DATABASE_URL`: `postgresql://[username]:[password]@[rds-endpoint]:5432/postgres` (replace with your RDS details)
   - `AWS_S3_BUCKET`: `waterforall-dev-cv-images` (or your bucket name)
   - *(Note: While your S3 bucket name isn't strictly a "secret", it's convenient to group all `.env` variables in Secrets Manager for your deployment. Also, `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` do not strictly need to be here if your deployment uses an IAM Task Role).*
5. Click **Next**.
6. **Secret name**: `waterforall-dev-secrets`.
7. Click **Next**, then **Store**.

## 5. IAM Roles (Identity and Access Management) - DONE

**Why do we need a new role?**
By default, your compute environment on AWS has zero permissions. It cannot securely read your secrets, upload to S3, or call Amazon Rekognition. Creating an IAM "Task Role" grants your application these exact permissions automatically and securely, entirely removing the need to hardcode `AWS_ACCESS_KEY_ID` in your code.

**Lambda vs. ECS (Architecture Decision)**
Based on `docs/plan.md`, our project relies on a Dockerized FastAPI backend that streams outputs to the frontend using **Server-Sent Events (SSE)**. **Amazon ECS (Fargate)** is strongly recommended over Lambda. Lambda has strict 15-minute execution limits and struggles with continuous SSE streaming, whereas ECS natively runs Docker containers and easily handles long-lived streaming connections.

**Steps for ECS Role:**
1. Navigate to the **IAM** console and select **Roles**.
2. Click **Create role**.
3. **Trusted entity type**: AWS service.
4. **Use case**: Select **Elastic Container Service Task** (specifically the `ecs-tasks.amazonaws.com` use case).
5. Click **Next**.
6. Add the following permissions policies (Using the "Most Privilege" approach for your Hackathon to avoid any permission blocks):
   - `AdministratorAccess` (This grants your container full god-mode over your AWS account, guaranteeing zero permission errors for S3, Rekognition, Secrets Manager, etc.)
   - `AmazonECSTaskExecutionRolePolicy` (Required so ECS can pull your Docker image from ECR and send logs to CloudWatch)
7. Click **Next**.
8. **Role name**: `WaterForAllComputeRole`.
9. Click **Create role**.

## 6. Local Development Environment Preparation - DONE

1. Ensure you have the **AWS CLI** installed locally (`aws --version`).
2. Run `aws configure` in your terminal and provide an IAM user's Access Key ID and Secret Access Key that has Administrator or sufficient privileges to push to ECR and deploy services.

---

Once these configurations are established in your AWS Console, you are ready to proceed with packaging the Docker container, pushing to ECR, and initiating the compute/API Gateway deployment.
