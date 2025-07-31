# Google Form Photo Upload Setup

The current issue is that Google Drive file uploads from forms are private by default, so they can't be displayed directly in the map.

## Solution Options:

### Option 1: Configure Form to Make Files Public (Recommended)

1. **In your Google Form:**
   - Go to Settings (gear icon)
   - Under "General" → "Collect email addresses" → **Enable this**
   - Under "General" → "Restrict to users in [your domain]" → **Disable this**

2. **In Google Drive (for existing files):**
   - Go to Google Drive
   - Find the folder "PACS Animal Registration Form (Responses)"
   - Right-click → Share → Change to "Anyone with the link can view"
   - Apply to all files in folder

3. **For new uploads (Apps Script solution):**
   Add this to your Apps Script to auto-share new files:

```javascript
function makeUploadedFilesPublic() {
  try {
    // Get the form responses folder
    const folderId = 'YOUR_FORM_FOLDER_ID'; // Replace with actual folder ID
    const folder = DriveApp.getFolderById(folderId);
    
    // Get all files modified in the last hour (new uploads)
    const files = folder.getFiles();
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
    
    while (files.hasNext()) {
      const file = files.next();
      if (file.getDateCreated() > oneHourAgo) {
        // Make file publicly viewable
        file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
        console.log('Made public:', file.getName());
      }
    }
  } catch (error) {
    console.error('Error making files public:', error);
  }
}
```

### Option 2: Use Alternative Image Hosting

Consider using:
- **Imgur API** - Free image hosting
- **Cloudinary** - Professional image management
- **Direct upload to GitHub repository** - Store images with code

### Option 3: Fallback Display (Current Implementation)

The map now shows:
- ✅ Direct image if accessible
- ✅ "View Photo" link if image fails to load
- ✅ Graceful degradation for private files

## Testing the Current Fix:

1. Generate new map: `./pacs-map generate`
2. Check popup - should show "View Photo" link if image doesn't load
3. Click link opens Google Drive file

## For Production:

The current implementation provides a good user experience even with private files, showing a clickable link when the direct image fails to load.