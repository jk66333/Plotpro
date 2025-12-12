# Monitoring & Alerting Guide for PlotPro VPS

To ensure stability and catch bottlenecks early, you should implement both **Real-time Monitoring** and **Automated Alerting**.

## Option 1: Netdata (Recommended for Real-time Visuals)
Netdata is a free, open-source tool that installs visually stunning real-time dashboards on your server with a single command. It has very low overhead.

### Installation
SSH into your server and run:
```bash
wget -O /tmp/netdata-kickstart.sh https://my-netdata.io/kickstart.sh && sh /tmp/netdata-kickstart.sh
```

### Accessing Dashboards
Visit: `http://YOUR_SERVER_IP:19999`
You will see real-time charts for:
- CPU Usage (Check for spikes during PDF generation)
- RAM Usage (Check for memory leaks)
- Disk I/O & Space

---

## Option 2: Custom Alert Script (Simple & Effective)
If you don't want external tools, use this simple script to check resources every 5 minutes and email you if something is wrong.

### 1. Create the Script
Create a file named `/root/monitor_server.sh` (or uploading the `monitor_resources.sh` provided).

### 2. Configure Cron Job
Run `crontab -e` and add this line to run every 5 minutes:
```bash
*/5 * * * * /bin/bash /root/monitor_server.sh >> /var/log/monitor.log 2>&1
```

---

## Option 3: External Uptime Check (Essential)
Use a free service like **UptimeRobot** or **Better Stack**.
1.  Create an account.
2.  Add a "HTTP Monitor" for `https://www.plotpro.in`.
3.  Add a generic "Keyword Monitor" that checks for a specific text on your login page (e.g., "Login").
    *   *Why?* Sometimes the server responds 200 OK but shows a database error page. Validating text ensures the app is actually loaded.

---

## What to Watch For (Thresholds)
- **CPU:** Standard is 10-30%. Alert if **> 85% for 5 minutes**.
- **RAM:** Linux caches files, so "Used" might look high. Look at **"Available"**. Alert if **< 500MB Available**.
- **Disk:** Alert if usage **> 90%**.
