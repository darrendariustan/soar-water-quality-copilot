# Part 12: Final Production Deployment Implementation Plan

This plan provides a beginner-friendly, step-by-step guide to deploying the WaterForAll backend to AWS using manual ClickOps (clicking through the AWS console) and the AWS CLI, followed by deploying the frontend to Vercel.

## User Review Required

> [!WARNING]
> **API Gateway vs Application Load Balancer (ALB)**
> We have formally replaced the API Gateway requirement with an Application Load Balancer (ALB). API Gateway has a strict 29-second connection timeout which breaks our Server-Sent Events (SSE) streaming for the chat assistant. The ALB natively supports long-lived HTTP connections required for SSE.

## Proposed Changes

### 1. Docker & Amazon ECR (Backend) via AWS CLI
We will package your local code into a Docker container and upload it to AWS. Based on your ECR repository, we will use your exact Account ID (`986682844768`), Region (`us-east-1`), and Repo name (`waterforall-cv`).

**Step-by-step:**
1. Open your terminal on your computer.
2. Authenticate Docker with your AWS account by running exactly this command:
   `aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 986682844768.dkr.ecr.us-east-1.amazonaws.com`
3. Build the Docker image from your project folder:
   `docker build -t waterforall-cv .`
4. Tag the image so it points to your AWS repository:
   `docker tag waterforall-cv:latest 986682844768.dkr.ecr.us-east-1.amazonaws.com/waterforall-cv:latest`
5. Push the image up to AWS:
   `docker push 986682844768.dkr.ecr.us-east-1.amazonaws.com/waterforall-cv:latest`

### 2. Networking & Security Groups (ClickOps)
We need to create "virtual firewalls" (Security Groups) to ensure the load balancer can talk to the container, and the container can talk to the database securely.

**Step-by-step:**
1. Log into the AWS Console and search for **EC2**.
2. On the left sidebar, scroll down to **Security Groups** and click **Create security group**.
3. **Create the ALB Security Group (`waterforall-alb-sg`):**
   - Name it `waterforall-alb-sg`.
   - Description: `Allows public HTTP internet traffic to the load balancer.`
   - Under Inbound rules, click **Add rule**. Choose Type: **HTTP** (Port 80) and Source: **Anywhere-IPv4** (`0.0.0.0/0`).
   - Click **Create security group**.
4. **Create the ECS Task Security Group (`waterforall-ecs-sg`):**
   - Click **Create security group** again. Name it `waterforall-ecs-sg`.
   - Description: `Allows internal port 8000 traffic strictly from the ALB security group.`
   - Under Inbound rules, click **Add rule**. Choose Type: **Custom TCP**, Port range: **8000**, and for Source, search for and select `waterforall-alb-sg`. (This ensures only the load balancer can access the backend container).
   - Click **Create security group**.
5. **Update the RDS Security Group (`waterforall-rds-sg`):**
   - Find your existing `waterforall-rds-sg` in the list and click on it.
   - Click **Edit inbound rules**.
   - Click **Add rule**. Choose Type: **PostgreSQL** (Port 5432). For Source, search for and select `waterforall-ecs-sg`. 
   - Click **Save rules**.

### 3. Application Load Balancer Setup (ClickOps)
The load balancer will give us a public URL and route internet traffic to our containers. We will keep port 8000 as it is the easiest configuration and requires no code changes.

**Step-by-step:**
1. In the EC2 console sidebar, under **Load Balancing**, click **Target Groups**.
2. Click **Create target group**.
   - Choose target type: **IP addresses**.
   - Target group name: `waterforall-tg`.
   - Protocol: **HTTP**, Port: **8000**.
   - VPC: Leave as default.
   - Click **Next**, then without adding any IPs, click **Create target group**.
3. In the sidebar, click **Load Balancers**.
4. Click **Create load balancer** and choose **Application Load Balancer**.
   - Load balancer name: `waterforall-alb`.
   - Scheme: **Internet-facing**.
   - Network mapping: Select your default VPC and check all the boxes for the Availability Zones.
   - Security groups: Remove the default one and select `waterforall-alb-sg`.
   - Listeners and routing: Ensure Protocol is HTTP, Port 80, and select the `waterforall-tg` target group for default action.
   - Click **Create load balancer**.
5. **How to retrieve the ALB URL:** Click on your new load balancer. In the Details tab, look for the **DNS name** (e.g., `waterforall-alb-1234.us-east-1.elb.amazonaws.com`). Copy this; this will be your backend API URL!

### 4. Amazon ECS with Fargate Setup (ClickOps)
This is where we run your Docker container in the cloud without managing servers.

**Step-by-step:**
1. Search for **ECS** (Elastic Container Service) in the top AWS search bar.
2. Click **Clusters** on the left, then **Create cluster**. Name it `waterforall-cluster` and choose **AWS Fargate** (serverless). Click Create.
3. Click **Task definitions** on the left, then **Create new task definition**.
   - Task definition family: `waterforall-task`.
   - Launch type: AWS Fargate.
   - Operating system/Architecture: Linux/X86_64.
   - Task role & Task execution role: Select the `WaterForAllComputeRole` you created earlier.
   - Container - 1:
     - Name: `backend`.
     - Image URI: Paste exactly `986682844768.dkr.ecr.us-east-1.amazonaws.com/waterforall-cv:latest`
     - Container port: **8000**, Protocol: TCP.
   - Environment variables: Add key-value pairs for `DATABASE_URL` (your RDS endpoint), `OPENAI_API_KEY`, `EXA_API_KEY`, `AWS_DEFAULT_REGION` (`us-east-1`), and `AWS_S3_BUCKET` (`waterforall-dev-cv-images`). *(Note: You don't need AWS_ACCESS_KEY_ID because the Task Role securely provides AWS permissions automatically!)*
   - Click **Create**.
4. Go back to your `waterforall-cluster` and in the Services tab, click **Create**.
   - Compute options: Launch type -> **Fargate**.
   - Application type: **Service**.
   - Task definition: Select `waterforall-task`.
   - Service name: `waterforall-service`.
   - Desired tasks: 1.
   - Networking: Select your default VPC, choose all subnets, and select the `waterforall-ecs-sg` security group. Ensure "Public IP" is turned **ON** so it can download the image from ECR over the internet.
   - Load balancing: Select Application Load Balancer. Choose the ALB you created, and select the container `backend:8000:8000` to route to the `waterforall-tg` target group.
   - Click **Create service**. Wait a few minutes for the task to reach the "RUNNING" state.

### 5. Database Migration (PostgreSQL)
We need to set up the tables inside your new AWS RDS database using your terminal.

**Step-by-step:**
1. Open your local terminal. Since you don't have `psql` installed, we will use Python (which you already have) to connect to the database and enable `pgvector`.
2. Run this exact command in your terminal. It uses your existing `uv` setup to connect to the database and run the command in one step:
   ```powershell
   uv run python -c "import psycopg2; conn=psycopg2.connect('postgresql://postgres:PUBwater4all@waterforall-db.cshrupbqalmb.us-east-1.rds.amazonaws.com:5432/postgres'); conn.autocommit=True; conn.cursor().execute('CREATE EXTENSION IF NOT EXISTS vector;'); print('pgvector successfully enabled!')"
   ```
   *(This connection works because your local IP was added to the `waterforall-rds-sg` security group).*
3. Wait for it to print "pgvector successfully enabled!".
4. Next, apply your database schemas. Open your local `.env` file and ensure the `DATABASE_URL` is pointing to your AWS RDS endpoint:
   `DATABASE_URL=postgresql://postgres:PUBwater4all@waterforall-db.cshrupbqalmb.us-east-1.rds.amazonaws.com:5432/postgres`
5. Finally, run your backend database setup script to build the tables in AWS. Since you are using Docker locally for your backend, you can run the script directly inside your running container:
   ```bash
   docker exec -it hackathon-backend-1 uv run python pipelines/ingest_knowledge.py
   ```
   *(Ensure your local `.env` file is updated and saved first, as the Docker container will read it).*
   This will push all the initial tables and knowledge straight into your live AWS database.

### 6. Vercel (Frontend)
Deploying the frontend Next.js app seamlessly.

**Step-by-step:**
1. From your Vercel Dashboard, click the white **Add New...** button in the top right and select **Project**.
2. Find `soar-water-quality-copilot` in your GitHub list and click **Import**.
3. **CRITICAL Configuration (Before Deploying):**
   - **Application Preset:** Vercel might auto-detect "FastAPI" by mistake because it sees your python code. Click the dropdown and change it to **Next.js**.
   - **Root Directory:** Click **Edit**, type exactly `src/frontend`, and click Save. *(This is extremely important because your Next.js frontend code is in that subfolder).*
4. **Environment Variables:**
   - Expand the Environment Variables dropdown.
   - Add the key: `NEXT_PUBLIC_API_URL`.
   - Add the value: Paste your **ALB DNS name** (e.g., `http://waterforall-alb-1234.us-east-1.elb.amazonaws.com`). Make sure it has `http://` at the beginning!
   - Click **Add**.
5. Click **Deploy**. Vercel will automatically build and host your frontend directly from your GitHub branch.

## Verification Plan

### Manual Verification
1. Open the public Vercel URL for your deployed Next.js app.
2. Try uploading a test strip image; ensure the backend returns the readings.
3. Test the chat interface; verify the text streams back token-by-token.
4. Verify results are saved by querying your RDS database.
