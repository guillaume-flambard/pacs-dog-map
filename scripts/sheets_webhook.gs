/**
 * Google Apps Script to trigger GitHub Action when sheet is edited
 * 
 * Setup Instructions:
 * 1. Open https://script.google.com/
 * 2. Create new project, paste this code
 * 3. Replace YOUR_GITHUB_TOKEN with your personal access token
 * 4. Save and set up onEdit trigger
 */

// Configuration
const GITHUB_OWNER = 'guillaume-flambard';
const GITHUB_REPO = 'pacs-dog-map';
const GITHUB_TOKEN = 'YOUR_GITHUB_TOKEN'; // Replace with your token
const WORKFLOW_ID = 'update-map.yml';

/**
 * Triggers when any cell in the sheet is edited
 */
function onEdit(e) {
  // Only trigger for the main data sheet
  const sheet = e.source.getActiveSheet();
  if (sheet.getName() !== 'List v2') {
    return;
  }
  
  // Add small delay to avoid multiple rapid triggers
  Utilities.sleep(2000);
  
  console.log('Sheet edited, triggering GitHub Action...');
  triggerGitHubAction();
}

/**
 * Manually trigger GitHub Action (for testing)
 */
function triggerGitHubAction() {
  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/${WORKFLOW_ID}/dispatches`;
  
  const payload = {
    ref: 'main',
    inputs: {
      trigger_source: 'google_sheets_webhook'
    }
  };
  
  const options = {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${GITHUB_TOKEN}`,
      'Accept': 'application/vnd.github+json',
      'Content-Type': 'application/json',
      'X-GitHub-Api-Version': '2022-11-28'
    },
    payload: JSON.stringify(payload)
  };
  
  try {
    const response = UrlFetchApp.fetch(url, options);
    
    if (response.getResponseCode() === 204) {
      console.log('✅ GitHub Action triggered successfully');
    } else {
      console.error('❌ Failed to trigger GitHub Action:', response.getContentText());
    }
  } catch (error) {
    console.error('❌ Error triggering GitHub Action:', error.toString());
  }
}

/**
 * Test function - run this manually to test the webhook
 */
function testWebhook() {
  console.log('Testing webhook...');
  triggerGitHubAction();
}