# Enterprise Employee Management DevOps Architecture

## 1. System Overview
The **Employee Management DevOps Platform** is designed for high availability, zero-downtime rolling deployments, strict security segmentation, and automated drift correction. It is deployed on AWS using **Terraform (IaC)**, provisioned with **Ansible**, continuously enforced by **Puppet**, and proactively monitored with **Nagios Core & NRPE**.

---

## 2. Infrastructure Architecture Diagram

```mermaid
flowchart TD
    subgraph Internet ["Public Internet"]
        User["End User / Browser"]
        Admin["DevOps Engineer / Admin"]
    end

    subgraph AWS_Cloud ["AWS Cloud (Region: us-east-1)"]
        subgraph VPC ["Custom VPC: 10.0.0.0/16"]
            
            subgraph Public_Subnets ["Public Subnets (Tier 1: 10.0.1.0/24, 10.0.2.0/24)"]
                IGW["Internet Gateway"]
                ALB["Application Load Balancer (ALB)"]
                NAT["NAT Gateway (Elastic IP)"]
                Nagios["Nagios Monitoring Server (10.0.1.80)"]
            end

            subgraph Private_App_Subnets ["Private App Subnets (Tier 2: 10.0.10.0/24, 10.0.11.0/24)"]
                subgraph ASG ["EC2 Auto Scaling Group (min 2, max 4)"]
                    App1["EC2 Instance 1\n(Nginx + Gunicorn + Flask)\n10.0.10.11"]
                    App2["EC2 Instance 2\n(Nginx + Gunicorn + Flask)\n10.0.11.12"]
                end
            end

            subgraph Private_DB_Subnets ["Private DB Subnets (Tier 3: 10.0.20.0/24, 10.0.21.0/24)"]
                subgraph RDS_Cluster ["Amazon RDS MySQL 8.0 (Multi-AZ)"]
                    PrimaryDB[("Primary MySQL DB\n10.0.20.15:3306")]
                    StandbyDB[("Standby Replica\nus-east-1b")]
                end
            end

        end
    end

    User -->|HTTPS :443 / HTTP :80| IGW
    Admin -->|SSH :22 via Bastion / VPN| NAT
    IGW --> ALB
    ALB -->|Reverse Proxy :5000| App1
    ALB -->|Reverse Proxy :5000| App2
    App1 -->|MySQL :3306| PrimaryDB
    App2 -->|MySQL :3306| PrimaryDB
    PrimaryDB -.->|Synchronous Replication| StandbyDB

    App1 -->|Outbound Package Updates| NAT
    App2 -->|Outbound Package Updates| NAT
    NAT --> IGW

    Nagios -.->|NRPE :5666 & HTTP :5000 /health| App1
    Nagios -.->|NRPE :5666 & HTTP :5000 /health| App2
    Nagios -.->|TCP :3306 Check| PrimaryDB
```

---

## 3. Network Segmentation & CIDR Breakdown

| Subnet Tier | CIDR Block | Availability Zone | Purpose | Route Table Target |
|:---|:---|:---|:---|:---|
| **Public Subnet 1** | `10.0.1.0/24` | `us-east-1a` | ALB, NAT Gateway | Internet Gateway (`igw`) |
| **Public Subnet 2** | `10.0.2.0/24` | `us-east-1b` | ALB Multi-AZ | Internet Gateway (`igw`) |
| **Private App 1** | `10.0.10.0/24` | `us-east-1a` | EC2 App Node 1 | NAT Gateway (`nat-gw`) |
| **Private App 2** | `10.0.11.0/24` | `us-east-1b` | EC2 App Node 2 | NAT Gateway (`nat-gw`) |
| **Private DB 1** | `10.0.20.0/24` | `us-east-1a` | Primary RDS MySQL | Local VPC Only (Isolated) |
| **Private DB 2** | `10.0.21.0/24` | `us-east-1b` | Standby RDS MySQL | Local VPC Only (Isolated) |

---

## 4. Security Model & Defense in Depth

1. **ALB Security Group**:
   - Ingress: `80` and `443` open to `0.0.0.0/0`.
   - Egress: Forwarding to EC2 App instances on port `5000`.
2. **EC2 Application Security Group**:
   - Ingress: Port `5000` is **only** reachable from the ALB Security Group ID. No direct public internet traffic reaches application instances.
   - Ingress: Port `22` (SSH) is locked down to authorized admin/bastion CIDRs (`var.admin_cidr`).
   - Egress: Outbound traffic routed via the NAT Gateway for OS patches and PyPI updates.
3. **RDS Database Security Group**:
   - Ingress: Port `3306` allowed **only** from the EC2 Application Security Group ID.
   - Egress: Restricted to VPC local CIDR.

---

## 5. Entity Relationship (ER) Data Model

```mermaid
erDiagram
    USERS {
        int id PK
        string username UK
        string email UK
        string password_hash
        string role
        datetime created_at
    }

    DEPARTMENTS {
        int id PK
        string name UK
        string code UK
        string description
        float budget
        datetime created_at
        datetime updated_at
    }

    EMPLOYEES {
        int id PK
        string first_name
        string last_name
        string email UK
        string phone
        date hire_date
        string job_title
        float salary
        string status
        int department_id FK
        datetime created_at
        datetime updated_at
    }

    DEPARTMENTS ||--o{ EMPLOYEES : "employs (1 to Many)"
```
