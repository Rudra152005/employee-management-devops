# DevOps Troubleshooting & Operations Runbook

This guide documents common incidents, root causes, and verified resolution steps across the application, infrastructure, configuration management, and monitoring tiers.

---

## 1. Application & Database Tier

### Issue 1: `502 Bad Gateway` on Nginx
- **Symptom**: Nginx returns HTTP 502 when browsing the application.
- **Root Cause**: Gunicorn process is either stopped, crashed due to an uncaught exception, or listening on an incorrect port/socket.
- **Resolution**:
  1. Inspect Gunicorn systemd service status:
     ```bash
     sudo systemctl status employee-app
     ```
  2. Inspect real-time logs via journalctl:
     ```bash
     sudo journalctl -u employee-app -n 50 -f
     ```
  3. Ensure Gunicorn is listening on `127.0.0.1:5000`:
     ```bash
     netstat -tlpn | grep 5000
     ```
  4. Restart application service:
     ```bash
     sudo systemctl restart employee-app
     ```

### Issue 2: Database Connection Timeout / `OperationalError: (2003, "Can't connect to MySQL server")`
- **Symptom**: Application fails health check `/health` reporting database disconnected.
- **Root Cause**: RDS Security Group does not allow ingress from EC2 Security Group, or credentials in `.env` are invalid.
- **Resolution**:
  1. Verify the RDS Security Group has rule allowing port `3306` from the EC2 Security Group ID (`sg-xxxx`).
  2. Test raw TCP connection from the EC2 instance:
     ```bash
     nc -zv <RDS_ENDPOINT> 3306
     ```
  3. Check `.env` database URI format:
     ```
     DATABASE_URL=mysql+pymysql://<DB_USER>:<DB_PASSWORD>@<DB_HOST>:3306/<DB_NAME>?charset=utf8mb4
     ```

---

## 2. Infrastructure (Terraform & AWS)

### Issue 3: Terraform State Lock Error (`Error acquiring the state lock`)
- **Symptom**: `terraform apply` fails indicating DynamoDB lock table is locked by another process ID.
- **Resolution**:
  ```bash
  terraform force-unlock <LOCK_ID>
  ```

### Issue 4: Target Group Reports EC2 Instances as `Unhealthy`
- **Symptom**: ALB returns `503 Service Temporarily Unavailable`.
- **Root Cause**: The health check endpoint `/health` returned non-200 or timed out.
- **Resolution**:
  1. SSH into the EC2 instance and run:
     ```bash
     curl -i http://127.0.0.1:5000/health
     ```
  2. Verify HTTP response is `200 OK` with JSON payload `{"status":"healthy","database":"connected"}`.
  3. Ensure EC2 Security Group ingress allows port `5000` from the ALB Security Group.

---

## 3. Configuration Management (Ansible & Puppet)

### Issue 5: Ansible `UNREACHABLE! Permission denied (publickey)`
- **Symptom**: Ansible playbook fails to connect to hosts.
- **Resolution**:
  1. Confirm the SSH key specified in `ansible/inventory/hosts.ini` exists and has correct permissions:
     ```bash
     chmod 400 ~/.ssh/devops_key.pem
     ```
  2. Test manual SSH connection:
     ```bash
     ssh -i ~/.ssh/devops_key.pem ubuntu@<IP>
     ```

### Issue 6: Puppet Certificate Mismatch (`certificate verify failed`)
- **Symptom**: Agent cannot pull catalog from master.
- **Resolution**:
  1. On the agent node:
     ```bash
     sudo rm -rf /etc/puppetlabs/puppet/ssl
     sudo puppet agent -t
     ```
  2. On the master node:
     ```bash
     sudo puppetserver ca list
     sudo puppetserver ca sign --certname <AGENT_HOSTNAME>
     ```

---

## 4. Monitoring (Nagios & NRPE)

### Issue 7: `CHECK_NRPE: Connection refused by host`
- **Symptom**: Nagios reports CRITICAL for all NRPE-based metrics.
- **Root Cause**: The NRPE daemon is not running on the target server, or `allowed_hosts` in `nrpe.cfg` does not include the Nagios server IP (`10.0.1.80`).
- **Resolution**:
  1. SSH into monitored host and edit `/etc/nagios/nrpe.cfg`:
     ```
     allowed_hosts=127.0.0.1,10.0.1.80
     ```
  2. Restart NRPE daemon:
     ```bash
     sudo systemctl restart nagios-nrpe-server
     ```
  3. Probe from Nagios server:
     ```bash
     /usr/lib/nagios/plugins/check_nrpe -H <TARGET_HOST_IP>
     ```
     *(Should return NRPE version)*
