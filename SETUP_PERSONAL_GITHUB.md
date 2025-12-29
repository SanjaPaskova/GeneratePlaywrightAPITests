# Quick Guide: Switch to Personal GitHub Account

## What You Need to Do

### Step 1: Update Git Config (This Repo Only)

Run these commands with YOUR personal info:

```bash
git config user.name "Your Personal Name"
git config user.email "your-personal-email@gmail.com"
```

**Example:**
```bash
git config user.name "Ervin Abedin"
git config user.email "ervin.personal@gmail.com"
```

### Step 2: Set Up Authentication

You have 2 options:

#### **Option A: Personal Access Token (Easiest)**

1. **Create Token:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Name it: "API Pronouts"
   - Check `repo` scope
   - Click "Generate token"
   - **COPY THE TOKEN** (starts with `ghp_...`)

2. **When Pushing:**
   - Username: Your personal GitHub username
   - Password: Paste the token (not your actual password!)

#### **Option B: SSH Keys (More Secure)**

1. **Check if you have SSH key:**
   ```bash
   dir %USERPROFILE%\.ssh\id_*.pub
   ```

2. **If no key, generate one:**
   ```bash
   ssh-keygen -t ed25519 -C "your-personal-email@gmail.com"
   ```
   (Press Enter to accept defaults)

3. **Copy your public key:**
   ```bash
   type %USERPROFILE%\.ssh\id_ed25519.pub
   ```

4. **Add to GitHub:**
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Paste the key and save

5. **Change remote to SSH:**
   ```bash
   git remote set-url origin git@github.com:SanjaPaskova/GeneratePlaywrightAPITests.git
   ```

### Step 3: Clear Old Credentials (If Needed)

If Git still uses your work account:

1. Open **Credential Manager** (search in Windows Start)
2. Go to **Windows Credentials**
3. Find `git:https://github.com`
4. Click it → **Remove**

### Step 4: Push!

```bash
git push -u origin feature/ui-frontend
```

---

## Quick Checklist

- [ ] Set personal name/email for this repo
- [ ] Create Personal Access Token OR set up SSH key
- [ ] Clear old credentials (if needed)
- [ ] Push the branch

---

## Need Your Info?

To help you set it up, I need:
1. Your personal GitHub username
2. Your personal email address
3. Your preference: Token (easier) or SSH (more secure)

Or you can do it yourself following the steps above! 🚀

