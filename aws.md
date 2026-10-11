# ClimateOps AWS EC2 Deployment Runbook

This is the project-specific AWS deployment runbook for ClimateOps. It
deploys the Next.js frontend and FastAPI backend to Amazon EC2 with Nginx as
the public reverse proxy. It covers the complete integration path for REST,
WebSocket, and Server-Sent Events (SSE) traffic.

Use this document for:

- Initial EC2 provisioning.
- Production configuration.
- Releases from an approved Git commit.
- Health checks and frontend/backend integration checks.
- Rollback, operations, and incident response.

This document contains placeholders intentionally. Replace them with the
actual AWS Region, hostname, account ID, and approved provider settings in
the deployment environment; never commit secret values to this repository.

## Deployment Contract

The following values are the fixed contract between the current application
and AWS:

| Component | Production value | Reason |
|---|---|---|
| Public application | `https://<public-hostname>` | Browser entry point |
| REST base | `https://<public-hostname>` | Frontend appends `/api/...` |
| WebSocket base | `wss://<public-hostname>` | Frontend appends `/api/monitoring/ws/incidents` |
| Nginx | `80` and `443` | Public HTTP/HTTPS |
| Next.js | `127.0.0.1:3000` | Private frontend upstream |
| FastAPI | `127.0.0.1:8000` | Private API upstream |
| Redis | `127.0.0.1:6379` | Private cache/worker dependency |
| Database | AWS DynamoDB | Production persistence |

Ports 3000, 8000, and 6379 must never be exposed through the EC2 security
group. Nginx is the only public application entry point.

## 1. Deployment Topology

```text
Internet
   |
   | HTTPS :443 / HTTP :80
   v
Nginx on EC2
   |-- /api/*, /health, /docs  -> FastAPI/Uvicorn on 127.0.0.1:8000
   |-- /api/monitoring/ws/*    -> WebSocket on FastAPI:8000
   |-- /api/monitoring/sse/*   -> SSE on FastAPI:8000
   `-- /*                      -> Next.js on 127.0.0.1:3000

FastAPI on EC2
   |-- DynamoDB (AWS-managed application data)
   |-- Redis (same EC2 host for the baseline deployment)
   `-- External climate and AI providers
```

This runbook describes a single-EC2 deployment, which is appropriate for the
current project and a small production workload. It is not highly available:
an EC2 failure interrupts both frontend and backend service. A later
high-availability architecture can use an Application Load Balancer, separate
ECS/EC2 services, ElastiCache for Redis, and a managed deployment pipeline.

## 2. Current Repository Assumptions

The deployment is based on the current project behavior:

- The backend starts with `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- The frontend starts with `npm run build` followed by `npm run start`.
- The frontend defaults to port 3000.
- The backend health endpoint is `GET /health`.
- The backend uses DynamoDB when `APP_ENV=production` and
  `AWS_DYNAMODB_ENDPOINT` is unset.
- The backend creates these DynamoDB tables during startup if they do not
  exist:
  `climatify-locations`, `climatify-observations`,
  `climatify-risk-assessments`, `climatify-incidents`,
  `climatify-incident-observations`, and `climatify-simulations`.
- The backend starts its monitoring loop as part of the application lifespan.
- The frontend uses `NEXT_PUBLIC_API_URL` for REST requests and
  `NEXT_PUBLIC_WS_URL` for WebSocket connections. These values are embedded
  into the Next.js build.

Do not use the development `backend/docker-compose.yml` as the production
deployment. It starts local DynamoDB, enables reload, publishes internal
ports, and is intended for development.

## 3. AWS Resources and Ownership

### Required

- One Ubuntu LTS EC2 instance with at least 2 vCPUs and 4 GB RAM for the
  baseline deployment.
- An Elastic IP or a DNS record that points to the instance.
- A DynamoDB table set in the same AWS Region as the EC2 instance.
- An IAM instance profile attached to EC2.
- A security group.

Record ownership before deployment:

```text
AWS account:              <account-id>
AWS Region:               <region>
Application owner:        <name/team>
Operations contact:       <email/on-call>
DNS owner:                <name/team>
Data owner:               <name/team>
Recovery decision-maker:  <name/team>
```

The owner is responsible for provider renewals, AWS billing, security
updates, data retention, and incident response.

### Recommended

- Route 53 for DNS.
- AWS Certificate Manager with an Application Load Balancer for managed TLS,
  or Certbot with Nginx if Nginx terminates TLS directly on EC2.
- CloudWatch Agent and alarms.
- EBS encryption, automatic snapshots, and instance recovery.
- ElastiCache for Redis when monitoring or traffic requires more than a
  single-instance setup.
- AWS Systems Manager Session Manager instead of exposing SSH publicly.

## 4. Before Provisioning

Choose and record:

```text
AWS Region:              <for example, ap-south-1>
Public DNS name:         climate.example.com
EC2 Ubuntu user:         ubuntu
Repository directory:    /opt/climateops
Backend port:             8000 (loopback only)
Frontend port:            3000 (loopback only)
Redis port:               6379 (loopback only)
```

The DNS name must resolve to the EC2 public address before requesting a
certificate. Do not put API keys in Git, shell history, screenshots, or the
frontend environment. Any variable beginning with `NEXT_PUBLIC_` is visible
to browser users and must not contain a secret.

### Application preflight

Before deploying, confirm:

- The PR containing the deployment documentation and application changes has
  been reviewed and merged, or the exact approved commit is recorded.
- Backend dependencies install from `backend/requirements.txt`.
- Frontend dependencies install with `npm ci` from the committed lockfile.
- `config/monitored_locations.json` is available on the host and contains
  only approved operational locations.
- Production provider accounts, quotas, attribution, and terms are approved.
- `SIMULATION_MODE_ENABLED` is intentionally chosen for the environment.
- A rollback commit and a configuration backup owner are known.

Do not deploy `backend/docker-compose.yml` to production. It is a local
development stack and starts local DynamoDB with development settings.

## 5. IAM Instance Profile

Attach an instance role to EC2 instead of setting
`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` on the server. The role needs
only the actions required by the deployment. At minimum, the current backend
needs DynamoDB table discovery, table creation, and data access.

Start with a region- and table-scoped policy similar to this, then reduce it
after observing actual CloudTrail usage:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ClimateOpsDynamoDB",
      "Effect": "Allow",
      "Action": [
        "dynamodb:ListTables",
        "dynamodb:DescribeTable",
        "dynamodb:CreateTable",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:<region>:<account-id>:table/climatify-*"
      ]
    }
  ]
}
```

`ListTables` cannot be resource-scoped by table ARN. If the application is
deployed with all tables already provisioned, remove `CreateTable` and keep
schema changes in a controlled infrastructure process. If S3 is enabled by
the application later, add access to only the configured bucket.

Verify the role from the host before starting the backend:

```bash
aws sts get-caller-identity
aws configure get region
aws dynamodb list-tables --region <region>
```

The returned account and region must match the intended deployment. Do not
work around an IAM error by adding administrator access.

## 6. Security Group

Allow only:

| Port | Source | Purpose |
|---|---|---|
| 80 | `0.0.0.0/0` | HTTP and certificate renewal/redirect |
| 443 | `0.0.0.0/0` | HTTPS application traffic |
| 22 | Your fixed admin IP only, or no public access with Session Manager | Administration |

Do **not** expose ports 3000, 8000, 6379, or any database port publicly.
Nginx and the system services communicate with these ports over loopback.

## 7. Create and Harden the EC2 Host

Connect using the distribution-provided user and then install the required
packages:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y nginx git python3.11 python3.11-venv python3-pip \
  build-essential redis-server certbot python3-certbot-nginx

node --version
```

Install Node.js 20 LTS if it is not already available. Use the official
NodeSource instructions or your organization-approved package repository;
verify that `node --version` is at least 20 before building the frontend.

Create a deployment user and application directory:

```bash
sudo adduser --system --group --home /opt/climateops climateops
sudo mkdir -p /opt/climateops
sudo chown -R climateops:climateops /opt/climateops
sudo systemctl enable --now redis-server
```

Apply the organization's Ubuntu hardening baseline, automatic security
updates, time synchronization, and disk monitoring. Confirm the instance
uses encrypted EBS storage and has an instance-recovery or backup policy.

Prefer AWS Systems Manager Session Manager. If SSH is required, use a
short-lived key, restrict port 22 to a fixed administrator IP, disable
password authentication, and do not share private keys.

Clone the repository as the deployment user:

```bash
sudo -u climateops git clone \
  https://github.com/marcosh2002/ClimateOps.git /opt/climateops
cd /opt/climateops
sudo -u climateops git checkout main
```

Use a reviewed release tag or a specific commit for production rather than
deploying an unreviewed branch tip. Record the deployed commit:

```bash
git rev-parse HEAD
git status --short
```

## 8. Configure the Backend

Create the environment file with permissions that allow only the service
account to read it:

```bash
sudo -u climateops cp /opt/climateops/backend/.env.example \
  /opt/climateops/backend/.env
sudo chmod 600 /opt/climateops/backend/.env
sudoedit /opt/climateops/backend/.env
```

Set production values. Keep the secret values private:

```dotenv
APP_ENV=production
APP_DEBUG=false
APP_HOST=127.0.0.1
APP_PORT=8000
SECRET_KEY=<32-or-more-character-random-secret>
CORS_ORIGINS=https://climate.example.com

AWS_REGION=<deployment-region>
AWS_DYNAMODB_ENDPOINT=
AWS_S3_BUCKET=<optional-approved-bucket>

GROQ_API_KEY=<secret>
GROQ_MODEL=llama-3.3-70b-versatile
REDIS_URL=redis://127.0.0.1:6379/0

OPENWEATHER_API_KEY=<secret>
NASA_POWER_API_KEY=<optional-secret>
GEONAMES_USERNAME=<approved-account>
OPENSTREETMAP_NOMINATIM_EMAIL=<operations-email>

IMD_API_BASE_URL=https://mausam.imd.gov.in
IMD_API_KEY=<optional-secret>
CWC_API_BASE_URL=<optional>
CWC_API_KEY=<optional-secret>

MONITORING_INTERVAL_MINUTES=5
MONITORED_LOCATIONS_CONFIG=/opt/climateops/backend/config/monitored_locations.json
SIMULATION_MODE_ENABLED=false
WEBSOCKET_HEARTBEAT_INTERVAL=30
SSE_RETRY_MS=3000
LOG_LEVEL=INFO
LOG_FORMAT=json
```

Important:

- Leave `AWS_DYNAMODB_ENDPOINT` empty in AWS. Setting it to a local endpoint
  makes the backend use local DynamoDB behavior.
- `APP_ENV=production` is required for the production DynamoDB path.
- `CORS_ORIGINS` must contain the exact public frontend origin, without a
  trailing slash.
- Generate `SECRET_KEY` with a password manager or
  `openssl rand -hex 32`; never use the example value.
- Review whether each provider key is required before adding it.

Install the backend and prepare its monitored-location configuration:

```bash
sudo -u climateops python3.11 -m venv /opt/climateops/backend/.venv
sudo -u climateops /opt/climateops/backend/.venv/bin/pip install \
  --upgrade pip
sudo -u climateops /opt/climateops/backend/.venv/bin/pip install \
  -r /opt/climateops/backend/requirements.txt

sudo -u climateops mkdir -p /opt/climateops/backend/config
# Add a reviewed config/monitored_locations.json file here.
```

Do not commit the production monitored-location file if it contains
restricted operational information. Validate that it is present before
starting the service.

### DynamoDB initialization

On the first production startup, the current backend calls
`init_dynamodb()` and creates missing tables using on-demand billing. Confirm
the six expected tables and their keys before accepting traffic. In a
controlled production account, pre-create and review the tables, then remove
`dynamodb:CreateTable` from the instance role.

The application currently creates tables at startup; this is convenient for
the initial deployment but should eventually be replaced by versioned
infrastructure migrations before a multi-instance rollout.

## 9. Configure the Frontend

Create the production environment file before building:

```bash
sudo -u climateops cp /opt/climateops/frontend/.env.example \
  /opt/climateops/frontend/.env.local
sudo chmod 600 /opt/climateops/frontend/.env.local
sudoedit /opt/climateops/frontend/.env.local
```

For a single public hostname, use same-origin paths:

```dotenv
NEXT_PUBLIC_API_URL=https://climate.example.com
NEXT_PUBLIC_WS_URL=wss://climate.example.com
NEXT_PUBLIC_GA_ID=
NEXT_PUBLIC_SENTRY_DSN=
NEXT_PUBLIC_SIMULATION_MODE=false
NEXT_PUBLIC_DEBUG=false
```

The frontend appends `/api/...` to the REST base and constructs
`/api/monitoring/ws/incidents` from the WebSocket base. Same-origin values
avoid exposing the private backend port and simplify CORS.

Do not set these values to `http://127.0.0.1:8000` or `ws://127.0.0.1:8000`
in a production build. In a user's browser, `127.0.0.1` means the user's own
computer, not the EC2 instance.

Build and verify the production bundle:

```bash
cd /opt/climateops/frontend
sudo -u climateops npm ci
sudo -u climateops npm run typecheck
sudo -u climateops npm run lint
sudo -u climateops npm run build
```

## 10. Run Services with systemd

Create the backend service:

```ini
# /etc/systemd/system/climateops-backend.service
[Unit]
Description=ClimateOps FastAPI backend
After=network-online.target redis-server.service
Wants=network-online.target

[Service]
Type=simple
User=climateops
Group=climateops
WorkingDirectory=/opt/climateops/backend
EnvironmentFile=/opt/climateops/backend/.env
ExecStart=/opt/climateops/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/climateops/backend

[Install]
WantedBy=multi-user.target
```

Create the frontend service:

```ini
# /etc/systemd/system/climateops-frontend.service
[Unit]
Description=ClimateOps Next.js frontend
After=network-online.target climateops-backend.service
Wants=network-online.target

[Service]
Type=simple
User=climateops
Group=climateops
WorkingDirectory=/opt/climateops/frontend
Environment=NODE_ENV=production
Environment=PORT=3000
ExecStart=/usr/bin/npm run start
Restart=always
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/climateops/frontend

[Install]
WantedBy=multi-user.target
```

Confirm the `npm` path with `command -v npm`; if Node was installed through a
version manager, use a stable system installation or an explicit absolute
path in `ExecStart`.

Enable and start both services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now climateops-backend
sudo systemctl enable --now climateops-frontend
sudo systemctl status climateops-backend climateops-frontend --no-pager
```

The backend starts its monitoring loop during application startup. Run only
one monitoring-loop instance in this single-EC2 topology. If the architecture
is later scaled horizontally, move monitoring to a singleton worker or
distributed scheduler before adding backend replicas.

## 11. Configure Nginx

Create `/etc/nginx/sites-available/climateops`:

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 80;
    listen [::]:80;
    server_name climate.example.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/monitoring/ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }

    location /api/monitoring/sse/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 3600s;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    location = /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        access_log off;
    }
}
```

Enable and validate it:

```bash
sudo ln -s /etc/nginx/sites-available/climateops \
  /etc/nginx/sites-enabled/climateops
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

The WebSocket and SSE locations must remain before the general `/api/`
location. The `proxy_pass` values intentionally preserve the request path.

### Request routing checklist

| Request | Expected upstream | Required behavior |
|---|---|---|
| `/` and frontend routes | `127.0.0.1:3000` | Next.js route refresh works |
| `/api/*` | `127.0.0.1:8000` | REST response passes through |
| `/health` | `127.0.0.1:8000` | Health response is reachable |
| `/api/monitoring/ws/*` | `127.0.0.1:8000` | Upgrade headers are preserved |
| `/api/monitoring/sse/*` | `127.0.0.1:8000` | Buffering is disabled |

Do not add a trailing path to the `proxy_pass` values in this configuration
without retesting route preservation. An incorrect trailing slash can change
the path received by FastAPI.

## 12. Enable HTTPS

After DNS points to the instance and HTTP works:

```bash
sudo certbot --nginx -d climate.example.com
sudo nginx -t
sudo systemctl reload nginx
sudo certbot renew --dry-run
```

Confirm that:

- HTTP redirects to HTTPS.
- The browser uses `https://` for REST and `wss://` for WebSocket.
- The certificate covers the exact hostname in the frontend environment.
- Renewal is scheduled by the installed Certbot timer.

## 13. First Deployment Verification

Run checks from the EC2 instance:

```bash
curl --fail http://127.0.0.1:8000/health
curl --fail http://127.0.0.1:3000
sudo systemctl --no-pager --full status climateops-backend
sudo systemctl --no-pager --full status climateops-frontend
sudo journalctl -u climateops-backend -n 100 --no-pager
sudo journalctl -u climateops-frontend -n 100 --no-pager
```

Run checks through the public hostname:

```bash
curl --fail https://climate.example.com/health
curl --fail https://climate.example.com/api/monitoring/status
```

In a browser, verify:

- Location search returns data.
- A climate dashboard loads without CORS errors.
- The emergency page connects to WebSocket updates.
- SSE updates are not buffered indefinitely.
- Browser refreshes work on frontend routes.
- Stale or unavailable provider data is shown explicitly.
- No secret appears in HTML, browser environment output, or logs.

### Integration acceptance criteria

The deployment is ready for users only when all of these pass:

- `GET /health` returns HTTP 200 through the public HTTPS hostname.
- A location search reaches FastAPI through `/api`.
- A climate-risk response loads in the frontend.
- An explanation request reaches the configured AI provider.
- The emergency view opens a WebSocket and reconnects after disconnect.
- The SSE endpoint streams without Nginx buffering.
- Browser refresh works on `/climate/<locationId>`, `/emergency`, and
  `/simulate`.
- The browser console contains no mixed-content, CORS, or failed WebSocket
  errors.
- Backend logs show production configuration and no missing required setting.
- DynamoDB contains the expected records after a verified application flow.
- Monitoring freshness and incident status are visible to the operator.

## 14. Updates and Rollback

Back up configuration before updating:

```bash
sudo cp /opt/climateops/backend/.env /opt/climateops/backend/.env.backup
sudo cp /opt/climateops/frontend/.env.local /opt/climateops/frontend/.env.local.backup
```

Deploy a reviewed commit:

```bash
cd /opt/climateops
sudo -u climateops git fetch origin
sudo -u climateops git checkout main
sudo -u climateops git pull --ff-only origin main

sudo -u climateops /opt/climateops/backend/.venv/bin/pip install \
  -r /opt/climateops/backend/requirements.txt
cd /opt/climateops/frontend
sudo -u climateops npm ci
sudo -u climateops npm run typecheck
sudo -u climateops npm run lint
sudo -u climateops npm run build

sudo systemctl restart climateops-backend climateops-frontend
sudo systemctl --no-pager status climateops-backend climateops-frontend
```

For a safer release, build the frontend before stopping the running service,
validate the backend dependencies first, and restart services only after the
new build succeeds. Never overwrite `.env`, certificates, or operational
configuration during a source update.

If the release fails, check out the previous known-good commit, rebuild the
frontend if necessary, and restart both services. Do not delete DynamoDB
tables as part of an application rollback.

## 15. Operations and Monitoring

Monitor at minimum:

- EC2 CPU, memory, disk, and system status.
- Nginx 4xx/5xx rates and access-log volume.
- Backend service restarts and `/health` availability.
- Provider failures, stale observations, and monitoring-cycle duration.
- DynamoDB throttling, errors, and consumed capacity.
- Redis availability and memory.
- TLS certificate expiry.

Use CloudWatch Logs or a controlled log shipping solution. Logs must not
contain API keys, authorization headers, personal data, or precise user
locations unless there is a documented operational need.

Configure alerts for repeated backend restarts, disk usage, failed health
checks, provider outage, stale monitoring data, and certificate renewal
failure. Keep a runbook with an owner and escalation path.

### Backup and recovery

- DynamoDB point-in-time recovery and deletion protection should be reviewed
  and enabled according to the data owner's retention policy.
- EBS snapshots must be encrypted and tested by restoring to a temporary
  instance.
- Keep a secure backup of service configuration without storing secrets in
  Git.
- Test recovery of the application, DNS, certificates, and monitored-location
  configuration separately.
- Record the maximum acceptable data loss and recovery time for incidents.

### Incident response

1. Confirm whether the issue affects frontend, backend, Nginx, AWS, or an
   external data provider.
2. Check public health, systemd status, Nginx logs, and backend logs.
3. If risk data is stale or unreliable, communicate that limitation and
   direct urgent decisions to official authorities.
4. Roll back to the last known-good application commit when appropriate.
5. Preserve timestamps and relevant logs, remove secrets, and document the
   cause and corrective action.

## 16. Common Problems

### The frontend still calls localhost

`NEXT_PUBLIC_*` values are build-time variables. Update
`frontend/.env.local` and run `npm run build` again before restarting
Next.js.

### REST requests work but WebSocket updates fail

Check that `NEXT_PUBLIC_WS_URL` uses `wss://` after HTTPS is enabled, the
Nginx WebSocket location is active, and the backend route is
`/api/monitoring/ws/incidents`.

### SSE updates are delayed

Confirm `proxy_buffering off` and the long `proxy_read_timeout` in the SSE
location. Check that the upstream service is producing events.

### The backend starts with local storage

Check `APP_ENV=production` and ensure `AWS_DYNAMODB_ENDPOINT` is empty. Verify
the EC2 role and region:

```bash
aws sts get-caller-identity
aws dynamodb list-tables --region <region>
```

### DynamoDB tables are missing

Inspect backend logs for startup permission or validation errors. The IAM
role must allow `ListTables`, `CreateTable` during first startup, and the
required item operations. For controlled environments, create and verify the
tables before starting the application.

### Nginx returns 502

Check service status and loopback listeners:

```bash
sudo ss -ltnp | grep -E ':(3000|8000)\b'
sudo journalctl -u climateops-backend -n 100 --no-pager
sudo journalctl -u climateops-frontend -n 100 --no-pager
```

## 17. Production Readiness Checklist

- [ ] EC2 is in the intended Region and has encrypted EBS storage.
- [ ] Security group exposes only 80/443 and restricted administration.
- [ ] IAM instance profile is attached; static AWS keys are not on disk.
- [ ] DynamoDB tables and billing mode have been reviewed.
- [ ] Redis persistence, memory, and recovery expectations are documented.
- [ ] Production `.env` files are outside Git and mode `600`.
- [ ] `APP_ENV=production`, `APP_DEBUG=false`, and simulation mode is reviewed.
- [ ] CORS allows only the production frontend origin.
- [ ] Nginx REST, WebSocket, and SSE routes pass configuration validation.
- [ ] HTTPS is active and renewal has been tested.
- [ ] Health, logs, provider freshness, and service restarts are monitored.
- [ ] Backups, rollback, incident response, and ownership are documented.
- [ ] Manual QA from [docs/manual-qa.md](./docs/manual-qa.md) has passed.
- [ ] Risk and emergency behavior has been reviewed using
  [docs/risk-and-safety.md](./docs/risk-and-safety.md).

## 18. Deployment Record

Complete this record outside the public repository or commit only the
non-sensitive fields:

```text
Deployment date:
AWS account:
AWS Region:
EC2 instance ID:
AMI/version:
Public hostname:
Deployed commit:
Backend service status:
Frontend service status:
Nginx configuration version:
TLS expiry:
DynamoDB tables verified:
Redis status:
Monitoring owner:
Rollback commit:
Last manual QA run:
Known limitations:
```

Never record passwords, private keys, API keys, session tokens, or complete
`.env` contents in this file or in an issue or pull request.
