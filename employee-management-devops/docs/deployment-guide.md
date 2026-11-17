# Complete Deployment & Operations Guide

This guide walks through all phases of deploying the **Employee Management DevOps Platform**, from local development and Docker containers to AWS infrastructure provisioning with Terraform, configuration management with Ansible and Puppet, and monitoring with Nagios.

---

## 1. Local Development Setup

### Prerequisites
- Python 3.10+ (Python 3.13 tested)
- pip and virtualenv
- Git

### Quickstart Steps
```bash
# 1. Navigate to the application directory
cd employee-management-devops/application

# 2. Create and activate a Python virtual environment
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# 3. Install application dependencies
pip install -r requirements.txt

# 4. Initialize database and seed sample data
python run.py init-db
python run.py seed

# 5. Launch the local development server
python run.py
```
Open your browser to `http://127.0.0.1:5000`
- **Username**: `admin`
- **Password**: `Admin@12345`

---

## 2. Docker Container Deployment

You can containerize the application using Docker:

### Build Container Image
```bash
docker build -t employee-management-app:latest -f application/Dockerfile application/
```

### Run Container Locally
```bash
docker run -d -p 5000:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=prod-secret-container-key \
  --name employee-app employee-management-app:latest
```

---

## 3. Terraform Cloud Infrastructure Provisioning

The `terraform/` directory provisions the entire AWS VPC, subnets across multiple AZs, NAT Gateway, Security Groups, ALB, Auto Scaling Group, and Amazon RDS MySQL Multi-AZ.

```bash
cd employee-management-devops/terraform

# 1. Initialize Terraform plugins
terraform init

# 2. Validate configuration syntax
terraform validate

# 3. Review planned cloud resources
terraform plan -out=tfplan.binary

# 4. Apply cloud architecture
terraform apply tfplan.binary
```

### Retrieving Infrastructure Outputs
```bash
terraform output alb_dns_name
terraform output rds_endpoint
```

---

## 4. Ansible Automated Configuration & Deployment

### Inventory Configuration
Update `ansible/inventory/hosts.ini` with your AWS instance private IPs or public bastion address.

### Run Master Setup Playbook
```bash
cd employee-management-devops/ansible

# Verify SSH connectivity
ansible all -i inventory/hosts.ini -m ping

# Execute end-to-end server configuration
ansible-playbook -i inventory/hosts.ini playbooks/site.yml
```

### Rolling Zero-Downtime Deployment
```bash
ansible-playbook -i inventory/hosts.ini playbooks/deploy-app.yml
```

---

## 5. Puppet Configuration Enforcement & Drift Correction

### Apply Catalog on Agents
```bash
# On the Puppet master:
puppet cert sign app-server-01.internal

# On agent nodes (run as cron or daemon every 30 mins):
puppet agent --test
```

### Simulating & Testing Self-Healing (Configuration Drift)
1. Intentionally stop the Nginx or App service:
   ```bash
   sudo systemctl stop nginx
   ```
2. Manually alter `/etc/nginx/sites-available/default`.
3. Trigger Puppet agent run:
   ```bash
   puppet agent --test
   ```
4. **Result**: Puppet detects file content discrepancy, restores original ERB template configuration, and restarts Nginx immediately.

---

## 6. Nagios Monitoring & Alerting Setup

1. Copy configuration files to your Nagios installation:
   ```bash
   sudo cp nagios/configurations/*.cfg /usr/local/nagios/etc/objects/
   ```
2. Verify Nagios syntax:
   ```bash
   sudo /usr/local/nagios/bin/nagios -v /usr/local/nagios/etc/nagios.cfg
   ```
3. Restart Nagios service:
   ```bash
   sudo systemctl restart nagios
   ```
4. Access web dashboard at `http://<NAGIOS_IP>/nagios` to observe live checks on hosts, services, and `/health` endpoints.
