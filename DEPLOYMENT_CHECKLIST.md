# 🚀 Phase 6: Deployment Checklist

Your bot is **8/8 tests passing** ✅ and ready to ship!

## Pre-Deployment: What You Need

- [ ] GitHub account (create if needed)
- [ ] Gmail account with 2FA enabled
- [ ] Telegram app installed
- [ ] Railway account (will create during deployment)

---

## Deployment Steps

### 1️⃣ GitHub Setup (10 min)

**Step 1.1: Create GitHub Account**
- [ ] Go to github.com
- [ ] Sign up with email
- [ ] Verify email

**Step 1.2: Create Repository**
- [ ] Log into GitHub
- [ ] Click "+" → "New repository"
- [ ] Name: `ryanair-price-tracker`
- [ ] Make it **Public**
- [ ] Add README
- [ ] Click "Create repository"
- [ ] **COPY the repository URL**

**Step 1.3: Push Code to GitHub**
```bash
cd ~/ryanair-price-tracker
git init
git add .
git commit -m "Initial commit: Ryanair price tracker bot"
git remote add origin <YOUR_REPO_URL>
git branch -M main
git push -u origin main
```
- [ ] Code uploaded to GitHub

---

### 2️⃣ Gmail Setup (5 min)

- [ ] Go to myaccount.google.com
- [ ] Click "Security"
- [ ] Enable "2-Step Verification"
- [ ] Scroll down to "App passwords"
- [ ] Select: Mail + Windows Computer
- [ ] Google generates password
- [ ] **COPY 16-character password**
- [ ] Save it: `_______________________`

---

### 3️⃣ Telegram Setup (5 min)

- [ ] Open Telegram
- [ ] Search: @BotFather
- [ ] Send: `/newbot`
- [ ] Give name: `RyanairPriceBot`
- [ ] Give username: `ryanair_price_bot_YOUR_NAME`
- [ ] **COPY BOT TOKEN**
- [ ] Save it: `_______________________`

**Get Chat ID:**
- [ ] Search for your bot
- [ ] Send any message to bot
- [ ] Go to: https://api.telegram.org/botTOKEN/getUpdates
- [ ] Find "chat"."id" in JSON
- [ ] **COPY CHAT ID**
- [ ] Save it: `_______________________`

---

### 4️⃣ Railway Deployment (15 min)

**Step 4.1: Create Railway Account**
- [ ] Go to railway.app
- [ ] Click "Start Project"
- [ ] Sign up with GitHub
- [ ] Authorize Railway

**Step 4.2: Deploy Project**
- [ ] Go to Railway dashboard
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub"
- [ ] Find `ryanair-price-tracker`
- [ ] Click to deploy
- [ ] Wait 2-3 minutes...

**Step 4.3: Set Environment Variables**
- [ ] Open project in Railway
- [ ] Click "Variables" tab
- [ ] Add:
  ```
  GMAIL_EMAIL=your-email@gmail.com
  GMAIL_PASSWORD=abcd efgh ijkl mnop
  TELEGRAM_BOT_TOKEN=123456789:ABCDeFGHIjklMnoPQrsTuVwXyZaBcDeFgH
  TELEGRAM_CHAT_ID=123456789
  PRICE_THRESHOLD=50
  ```
- [ ] Click "Save"

---

### 5️⃣ Verify Deployment (5 min)

**In Railway Dashboard:**
- [ ] Status shows "RUNNING" (green)
- [ ] Click "Logs" tab
- [ ] See: `✅ Scheduler started`
- [ ] See: `💡 Bot is ready!`

**Test Notifications (optional - wait up to 1 hour for first check):**
- [ ] Check Gmail inbox for price alert
- [ ] Check Telegram for bot message

---

## 🎉 You're Live!

✅ Bot running 24/7 on Railway
✅ Checks prices every hour
✅ Sends email alerts
✅ Sends Telegram messages
✅ Your Mac can stay off

---

## 📝 Quick Reference

**View Logs:**
```
Railway Dashboard → Project → Logs
```

**Change Threshold:**
```
Railway Dashboard → Variables → PRICE_THRESHOLD = 40
```

**Add New Route:**
```
Edit config.py locally → Push to GitHub → Railway auto-deploys
```

**Export Data:**
```bash
python exporter.py
```

**Test Locally (before deployment):**
```bash
python final_verification.py
python dashboard.py  # Visit localhost:5000
```

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot not running | Check Railway logs for errors |
| No notifications | Verify credentials in Railway Variables |
| Not seeing logs | Railway → Project → Logs tab |
| Price not updating | Wait 1 hour or check logs for scraper errors |

---

## 📚 Full Docs

- Read: `PHASE6_DEPLOYMENT.md` (detailed step-by-step)
- Test: `final_verification.py` (8/8 tests passing)
- View: `PHASE1-5_SUMMARY.md` files for component details

---

**All set? Ready to deploy?** 🚀

Just follow the checklist above and you'll have your bot running in the cloud!

**Questions?** Everything is in PHASE6_DEPLOYMENT.md
