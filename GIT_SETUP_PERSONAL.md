# Setting Up Personal GitHub Account

## Current Configuration
Your Git is currently configured with:
- **Name**: Ervin Abedin
- **Email**: eabedin@comply.com (work account)

## Step-by-Step Guide

### Step 1: Check Your Personal GitHub Username
Do you know your personal GitHub username? You'll need it for the next steps.

### Step 2: Update Git Config for This Repo Only (Recommended)

**Option A: Set for this repository only** (keeps work config global)
```bash
git config user.name "Your Personal Name"
git config user.email "your-personal-email@gmail.com"
```

**Option B: Change global config** (affects all repos)
```bash
git config --global user.name "Your Personal Name"
git config --global user.email "your-personal-email@gmail.com"
```

### Step 3: Set Up Personal GitHub Authentication

#### Option 1: Personal Access Token (PAT) - Recommended

1. **Create Token on GitHub:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Name: "API Pronouts Project"
   - Select scopes: `repo` (full control)
   - Click "Generate token"
   - **Copy the token** (you won't see it again!)

2. **Use Token When Pushing:**
   - When Git asks for password, use the token instead
   - Or configure credential helper to store it

#### Option 2: SSH Keys (More Secure)

1. **Check if you have SSH keys:**
   ```bash
   ls ~/.ssh/id_*.pub
   ```
   Or on Windows:
   ```bash
   dir %USERPROFILE%\.ssh\id_*.pub
   ```

2. **Generate SSH key if needed:**
   ```bash
   ssh-keygen -t ed25519 -C "your-personal-email@gmail.com"
   ```

3. **Add SSH key to GitHub:**
   - Copy public key: `cat ~/.ssh/id_ed25519.pub`
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Paste and save

4. **Change remote to SSH:**
   ```bash
   git remote set-url origin git@github.com:SanjaPaskova/GeneratePlaywrightAPITests.git
   ```

### Step 4: Clear Cached Credentials (If Needed)

If Git is using cached work credentials:

**Windows Credential Manager:**
1. Open "Credential Manager" (search in Start menu)
2. Go to "Windows Credentials"
3. Find `git:https://github.com`
4. Remove or edit it

**Or via command:**
```bash
git credential-manager-core erase
# Then enter:
# protocol=https
# host=github.com
# (Press Enter twice)
```

### Step 5: Push with Personal Account

After setting up authentication:
```bash
git push -u origin feature/ui-frontend
```

When prompted:
- **Username**: Your personal GitHub username
- **Password**: Your Personal Access Token (not your password!)

---

## Quick Commands Reference

```bash
# Check current config
git config user.name
git config user.email

# Set for this repo only
git config user.name "Your Name"
git config user.email "your-email@gmail.com"

# Check remote URL
git remote -v

# Change remote to SSH (if using SSH)
git remote set-url origin git@github.com:SanjaPaskova/GeneratePlaywrightAPITests.git

# Push
git push -u origin feature/ui-frontend
```

---

## Need Help?

Tell me:
1. Your personal GitHub username
2. Your personal email
3. Whether you want to use HTTPS (token) or SSH

I can help you set it up!

