# Capacity & Scalability Report for PlotPro SaaS

**Server Specifications:**
- **CPU:** 2 vCPU
- **RAM:** 8GB
- **Storage:** Standard SSD (Assumed)

## 1. Executive Summary
Your current Virtual Machine (VM) is suitable for a **Small-to-Medium usage** scenario.
- **Max Registered Tenants:** ~100-300 (assuming sporadic usage).
- **Max Active Tenants (Daily):** ~50.
- **Max Concurrent Users:** ~20 (browsing/editing).
- **Critical Bottleneck:** PDF Generation (Receipts/Commissions).

---

## 2. Capacity Breakdown

### A. Memory (RAM) - 8GB
Your capacity is primarily determined by how many processes can run simultaneously.

| Component | Usage per Instance | instances | Total Usage | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **System/OS** | 500 MB | 1 | 0.5 GB | Base overhead |
| **Nginx** | 50 MB | 1 | 0.05 GB | Negligible |
| **MySQL** | 1.5 GB | 1 | 1.5 GB | Buffer pool shared across all tenant DBs |
| **Gunicorn (App)**| 200 MB | 4 Workers | 0.8 GB | Python/Flask overhead |
| **Playwright** | 300 MB | 4 Workers | 1.2 GB | **Heavy!** Spawns Chromium per PDF request |
| **Available Buffer**| | | **~4.0 GB** | Safety margin / File caching |

**Conclusion:** RAM is **NOT** your immediate bottleneck. You have enough RAM to handle the database and web workers comfortably.

### B. CPU (Processing) - 2 vCores
This is your **Hard Limit**.
- **Web Browsing:** Light CPU usage. 2 cores can handle ~50-100 requests/sec.
- **PDF Generation:** **EXTREMELY HEAVY**.
    - Generating 1 PDF uses ~80-100% of 1 CPU core for 2-5 seconds.
    - With 2 Cores, you can effectively generate **only 2 PDFs simultaneously**.
    - If 4 people try to download a receipt at the exact same second, the 3rd and 4th person will experience a 5-10 second delay (or timeout).

---

## 3. Scaling Limits

### Scenario 1: Typical Usage (browsing, viewing plots, sporadic data entry)
- **Capacity:** The server can handle **50+ active tenants** logged in simultaneously.
- **Reasoning:** Most users are just reading data from MySQL, which is very fast and efficient.

### Scenario 2: Heavy Usage (End of Month / Mass PDF Printing)
- **Capacity:** Critical danger zone if **>3 tenants** generate PDFs simultaneously.
- **Risk:** CPU spikes to 100%, web pages become slow for *everyone* (including other tenants).
- **Hard Limit:** ~5-10 concurrent PDF generations per minute.

---

## 4. Recommendations for Growth

### Immediate Optimizations (No Cost)
1.  **Gunicorn Workers:** Stick to **3-4 workers**. Do not increase this number. More workers will just fight for the same 2 CPU cores and slow everything down.
2.  **Swap File:** Ensure you have a 4GB Swap file enabled as a safety net for RAM spikes.

### Future Upgrades (If you exceed 50 active tenants)
1.  **Upgrade VPS CPU**: Moving to **4 vCPU** will double your PDF capacity.
2.  **Offload PDF Generation**: This is the best long-term fix.
    - Instead of generating PDFs on the *Web Server* (blocking the user), use a **Queue System (Celery)**.
    - The user clicks "Download", the server says "Processing...", and a background worker picks it up.
    - This keeps the website fast for everyone else.

### Database Limit
- **File Limit:** Linux has a limit on open files. With "File-Per-Table" (InnoDB default), 300 tenants * 50 tables = 15,000 files.
- **Action:** Ensure `ulimit -n` is high (e.g., 65535) in your server config. 300 tenants is safe; 1000+ might require tuning.

## Final Verdict
**Your current setup is perfectly adequate for launching and growing your first 50 paying customers.** Monitor CPU usage during business hours. If it consistently hits >80%, upgrade to 4 vCores.
