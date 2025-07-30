# 🚀 PACS Dog Map - Quick Setup Guide

## Step 1: Publish Your Google Sheet

Your Google Sheet needs to be published to the web for the system to access it automatically.

### Instructions:
1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1vNW1GtXhWHyVrGJmIEAnlzWQp_QvtfMRD3hzbgYmK9w/edit
2. Click **File** → **Share** → **Publish to web**
3. In the dialog:
   - **Link tab**: Select "Entire Document" or your specific sheet
   - **Embed tab**: Choose **CSV** format
   - Click **Publish**
4. Copy the published CSV link (it will look like: `https://docs.google.com/spreadsheets/d/1vNW1GtXhWHyVrGJmIEAnlzWQp_QvtfMRD3hzbgYmK9w/export?format=csv&gid=1076834206`)

## Step 2: Test the Data Sync

Once published, test the automatic sync:

```bash
python google_sheets_sync.py
```

This will:
- ✅ Download your latest data
- ✅ Fix any coordinate issues
- ✅ Generate the updated map
- ✅ Save to `data_from_sheets.csv`

## Step 3: Enable GitHub Pages

1. Go to your repository Settings
2. Scroll to **Pages** section
3. Set source to **Deploy from a branch**
4. Choose **main** branch, **/ (root)** folder
5. Click **Save**

Your map will be available at: `https://yourusername.github.io/pacs-dog-map/`

## Step 4: Set Up Automatic Updates

The GitHub Action is already configured! It will automatically:
- ✅ Update the map when you push changes to CSV files
- ✅ Run daily at 2 PM Thailand time
- ✅ Deploy to GitHub Pages automatically

## Step 5: Test Everything

Run the comprehensive test:

```bash
python test_system.py
```

## 🎯 Quick Commands for Daily Use

```bash
# Sync latest data from Google Sheets
python google_sheets_sync.py

# List pending animals for field work
python batch_operations.py --list

# Show priority order (pregnant animals first)
python batch_operations.py --priority

# Mark animals as completed after field work
python batch_operations.py --complete 0 1 2  # Replace with actual row IDs
```

## 📱 For Volunteers & Field Workers

### WhatsApp Message Template:
```
🐕 NEW DOG REPORT
📍 Location: Thong Sala Market
🗺️ Maps: [paste Google Maps link]
🔢 Count: 2
⚧ Sex: Both
🎂 Age: Adult
😊 Mood: Friendly
🤰 Pregnant: No
📞 Reporter: Alaska
📱 Phone: 0622355014
💬 Notes: Behind the main market entrance
```

### Quick Data Entry:
1. **Take photo** of animal(s)
2. **Drop pin** on Google Maps
3. **Copy share link** from Google Maps
4. **Add row** to Google Sheet or use WhatsApp template
5. **System auto-updates** map within 24 hours

## 🆘 Troubleshooting

### If sync fails:
- Make sure Google Sheet is published to web
- Check the sheet has the right column names
- Verify internet connection

### If map doesn't update:
- Check GitHub Actions tab for any errors
- Make sure GitHub Pages is enabled
- Try manual generation: `python generate_enhanced_map.py`

### If coordinates are missing:
- Make sure Google Maps links are in correct format
- Run: `python fix_coordinates.py` to repair data

## 🎉 You're All Set!

Your PACS Dog Map is now a professional-grade rescue management system that will:
- ✅ **Save hours** of manual work
- ✅ **Prioritize** pregnant animals automatically  
- ✅ **Track progress** with real-time statistics
- ✅ **Scale** with your rescue operations

Share the map link with your volunteers and watch your sterilization efforts become more efficient! 🐕💙