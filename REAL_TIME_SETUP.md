# 🚀 Real-Time Google Sheets Sync Setup

This guide will set up automatic map updates whenever you edit your Google Sheets.

## 📋 Prerequisites

1. ✅ Your Google Sheets is publicly accessible
2. ✅ GitHub Actions workflow is working
3. ✅ GitHub Pages is configured to use "GitHub Actions" as source

## 🔧 Setup Steps

### Step 1: Create GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Set expiration to "No expiration" 
4. Check these scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
5. Click "Generate token"
6. **COPY THE TOKEN** - you won't see it again!

### Step 2: Set up Google Apps Script

1. **Open**: https://script.google.com/
2. **Create new project**
3. **Delete** the default code
4. **Copy and paste** the code from `scripts/sheets_webhook.gs`
5. **Replace `YOUR_GITHUB_TOKEN`** with your actual token from Step 1
6. **Save** the project (Ctrl+S)
7. **Rename** project to "PACS Dog Map Webhook"

### Step 3: Configure the Trigger

1. In Google Apps Script, click the **⏰ Triggers** icon (left sidebar)
2. Click **"+ Add Trigger"**
3. Configure:
   - **Function to run**: `onEdit`
   - **Event source**: `From spreadsheet`
   - **Event type**: `On edit`
4. Click **"Save"**
5. **Authorize** the script when prompted

### Step 4: Link to Your Spreadsheet

1. In Google Apps Script, click the **+** next to "Libraries"
2. Instead, click **Resources** → **Current project's libraries**
3. Actually, easier way:
   - Click **⚙️ Project Settings**
   - Under "Script Properties", click **"Add script property"**
   - Leave empty for now, we'll link differently...

**Better approach:**
1. **Open your Google Sheets**: https://docs.google.com/spreadsheets/d/1vNW1GtXhWHyVrGJmIEAnlzWQp_QvtfMRD3hzbgYmK9w/edit
2. Click **Extensions** → **Apps Script**
3. **Delete** the default code
4. **Paste** the webhook code from `scripts/sheets_webhook.gs`
5. **Replace** `YOUR_GITHUB_TOKEN` with your token
6. **Save** (Ctrl+S)

### Step 5: Set up the Trigger (In Sheet's Script)

1. Click the **⏰ Triggers** icon
2. Click **"+ Add Trigger"**
3. Configure:
   - **Function**: `onEdit`
   - **Event source**: `From spreadsheet`
   - **Event type**: `On edit`
4. **Save** and **authorize**

### Step 6: Test the Setup

1. In the Apps Script editor, click **▶ Run** next to `testWebhook`
2. Check the **Execution log** - should see "✅ GitHub Action triggered successfully"
3. Go to your GitHub Actions page to see if the workflow started
4. Make a test edit in your Google Sheets
5. Check if the workflow triggers automatically

## 🔥 How It Works

```
Google Sheets Edit → Apps Script onEdit() → GitHub API → Trigger Workflow → Sync & Deploy → Live Map Updated
```

**Timeline**: 2-4 minutes from sheet edit to live map update

## ⚡ Alternative: Zapier/n8n Integration

If Google Apps Script doesn't work, you can use:

### Option A: Zapier
1. **Trigger**: Google Sheets "New or Updated Spreadsheet Row"
2. **Action**: Webhooks "POST" to GitHub API
3. **URL**: `https://api.github.com/repos/guillaume-flambard/pacs-dog-map/actions/workflows/update-map.yml/dispatches`

### Option B: n8n (Free)
1. **Google Sheets Trigger** node
2. **HTTP Request** node to GitHub API
3. Self-host or use n8n.cloud free tier

## 🐛 Troubleshooting

### Script Authorization Issues
- Make sure you authorize the script when prompted
- Check that the GitHub token has correct permissions

### Workflow Not Triggering
- Verify the GitHub token is valid
- Check GitHub Actions tab for any error messages
- Make sure repository name is exactly `pacs-dog-map`

### Too Many Triggers
- The script includes a 2-second delay to prevent rapid firing
- Only triggers on the "List v2" sheet tab

## 🎯 Expected Behavior

After setup:
1. ✅ Edit any cell in your Google Sheets
2. ✅ Wait 30 seconds, see workflow start in GitHub Actions  
3. ✅ Wait 2-3 minutes total, see changes on live map
4. ✅ No manual intervention needed!

Your PACS Dog Map will now update in real-time! 🎉