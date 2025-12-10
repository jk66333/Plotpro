# Infrastructure Recommendations for PlotPro SaaS

Since you are running a **Multi-Tenant SaaS with Isolated Databases**, your resource needs are slightly higher than a standard app. Specifically:
1.  **MySQL Overhead**: Managing many separate databases (even if small) consumes more RAM and file descriptors than a single database.
2.  **PDF Generation (Playwright)**: Generating receipts uses a Headless Browser (Chromium). This is **CPU and RAM intensive**. If 2-3 users generate a receipt at the exact same second, a small server might freeze.

## Recommended VM Sizing

### 1. Starter Tier (1 - 10 Clients)
*Suitable for initial launch and onboarding first few clients.*
- **CPU**: 2 vCPUs
- **RAM**: 4 GB (Minimum required for smooth Playwright + MySQL operation)
- **Storage**: 25 GB+ NVMe SSD (Databases need fast storage)
- **OS**: Ubuntu 22.04 LTS
- **Estimated Cost**: ~$20-25/month (DigitalOcean, AWS t3.medium, or similar)

### 2. Growth Tier (10 - 50 Clients)
*Recommended once you have active daily traffic.*
- **CPU**: 4 vCPUs
- **RAM**: 8 GB
- **Storage**: 50 GB+ NVMe SSD
- **Why upgrade?** More RAM allows MySQL to cache more data, resulting in faster searches and reports. More CPU handles simultaneous PDF generation better.

### 3. Scale Tier (50+ Clients)
*At this stage, we recommend splitting the server.*
- **Server A (App Only)**: 4 vCPU / 8 GB RAM (Runs Flask + Playwright)
- **Server B (Database Only)**: 4 vCPU / 16 GB RAM (Runs MySQL optimized for many tables)

## Critical Optimization Checklist
Since you are managing infrastructure yourself, you **must** configure these settings to avoid crashes:

1.  **Swap File**: Create a 4GB Swap file. This prevents the server from crashing (OOM Killer) if a PDF generation spikes RAM usage.
    ```bash
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    ```

2.  **MySQL Connections**:
    In `my.cnf`, ensure `max_connections` is high enough (e.g., 200) but not too high to exhaust RAM.

3.  **PDF Queue (Future Optimization)**:
    Currently, PDFs are generated "on the fly". If you get 100+ clients, we should move this to a "Background Worker" (e.g., Celery) so the website never slows down.

## Summary
**Start with 2 vCPU / 4 GB RAM.** Do not try to run this on a 1GB RAM micro-instance; the database or PDF generator will crash.
