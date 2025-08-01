# 🐾 PACS Dog Map – Professional Animal Sterilization Tracker

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**A professional, scalable system for tracking dogs and cats that need sterilization across Koh Phangan, Thailand.**

Built for local rescue organizations like [PACS](https://www.pacsthailand.com/), this system provides enterprise-grade features while maintaining simplicity and accessibility for field workers and volunteers.

## 🌍 Live Map

👉 **[View the interactive map here](https://your-username.github.io/pacs-dogs-map/)**  
_(Replace with your actual GitHub Pages link)_

### 🎯 Map Features:
- **Color-coded priorities**: Red (pregnant), Orange (wild), Blue (standard), Green (completed)
- **Advanced filtering**: By status, temperament, urgency level
- **Rich popups**: Photos, contact info, detailed location data
- **Statistics dashboard**: Real-time counts and progress tracking
- **Mobile-optimized**: Works perfectly on phones and tablets

---

## 📥 Enhanced Data Collection

### Multiple Collection Methods:

#### 🔥 **Google Sheets Integration** (Recommended)
- Direct sync from [your Google Sheet](https://docs.google.com/spreadsheets/d/1vNW1GtXhWHyVrGJmIEAnlzWQp_QvtfMRD3hzbgYmK9w/edit)
- Auto-coordinate extraction from Google Maps links
- Real-time updates without manual CSV exports

#### 📱 **WhatsApp Integration**
- Structured message templates for volunteers
- Optional n8n automation for parsing messages
- QR codes for quick form access

#### 📋 **Web Forms**
- Google Forms integration
- Mobile-friendly data entry
- Photo upload support

### Required Data Fields:
- 📍 **Location**: Area name + Google Maps link
- 🐕 **Animal Type**: Dog/Cat + count
- ⚧ **Demographics**: Sex, age, pregnancy status
- 😊 **Temperament**: Friendly/Wild/Cautious/Aggressive
- 📷 **Photo**: Optional but recommended
- 📞 **Contact**: Name and phone for coordination
- 🏷️ **Status**: Pending/Completed tracking

---

## 🚀 Advanced Features

### 🔄 **Automated Workflows**
- **GitHub Actions**: Auto-regenerate map when data changes
- **Priority Detection**: Auto-flag pregnant animals as high priority
- **Batch Operations**: Mark multiple animals as completed
- **Statistics Tracking**: Monitor progress over time

### 🛠 **Management Tools**

#### Batch Operations Script:
```bash
# List all pending animals
python batch_operations.py --list

# Show priority order for field work
python batch_operations.py --priority

# Mark animals as completed
python batch_operations.py --complete 0 1 2
```

#### Google Sheets Sync:
```bash
# Download latest data and generate map
python google_sheets_sync.py
```

---

## 📁 Project Structure

```
pacs-dog-map/
├── src/pacs_map/          # Main application code
│   ├── __init__.py        # Package initialization
│   ├── cli.py             # Command-line interface
│   ├── config.py          # Configuration management
│   ├── core.py            # Map generation engine
│   ├── data.py            # Data management
│   ├── coordinates.py     # Coordinate extraction
│   └── operations.py      # Batch operations
├── tests/                 # Comprehensive test suite
│   ├── test_coordinates.py
│   ├── test_data.py
│   ├── test_cli.py
│   └── test_integration.py
├── scripts/               # Legacy/utility scripts
├── data/                  # Data files (CSV, backups)
├── web/                   # Generated web files
├── docs/                  # Documentation
├── .github/workflows/     # CI/CD automation
├── pacs-map              # Main CLI entry point
├── pyproject.toml        # Project configuration
├── Makefile              # Development commands
└── README.md             # This file
```

## 🛠 Tech Stack

### Core Technologies:
- **Python 3.8+**: Modern, type-hinted codebase
- **Pandas**: Data processing and analysis
- **Folium/Leaflet**: Interactive mapping with clustering
- **Click**: Professional CLI interface
- **Pytest**: Comprehensive testing framework

### Infrastructure:
- **GitHub Actions**: Automated CI/CD and deployments
- **GitHub Pages**: Free hosting and distribution
- **Docker**: Containerized deployment (optional)

### Integration Options:
- **Google Sheets API**: Direct data synchronization
- **WhatsApp Business API**: Message automation
- **n8n/Zapier**: Workflow automation
- **REST APIs**: External system integration

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/pacs-dog-map.git
cd pacs-dog-map

# Install the package
make install

# Set up development environment (optional)
make setup-dev
```

### Configuration

All service IDs and settings are centralized in one place for easy management:

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your actual service IDs
nano .env
```

#### 📋 Required Configuration

**Google Sheets** (from your form responses sheet):
- `GOOGLE_SHEET_ID`: Document ID from URL
- `GOOGLE_SHEET_GID`: Sheet tab ID (gid parameter)  
- `GOOGLE_SHEET_PUBLISHED_ID`: Published CSV ID (starts with 2PACX)

**Cloudinary** (for photo uploads):
- `CLOUDINARY_CLOUD_NAME`: Your cloud name
- `CLOUDINARY_UPLOAD_PRESET`: Upload preset name

**Map Settings**:
- `MAP_CENTER_LAT/LNG`: Default map center coordinates
- `MAP_ZOOM`: Default zoom level

> **🔄 Easy Switching**: Change any service (form, sheet, Cloudinary) by updating the `.env` file - no code changes needed!

#### 🔒 **Security Note**
- **`.env.example`** ✅ **Public** - Template with example values (safe to commit)
- **`.env`** 🔒 **Private** - Your actual IDs (automatically gitignored)
- **`config.py`** ✅ **Public** - Code structure (safe to commit)

### Basic Usage

```bash
# Sync data from Google Sheets
./pacs-map sync

# Generate interactive map  
./pacs-map generate

# View statistics
./pacs-map stats

# List pending animals
./pacs-map list --pending

# Mark animals as completed
./pacs-map complete 0 1 2

# Generate field report
./pacs-map report
```

---

## 🎯 Priority Management System

The system automatically prioritizes animals based on:

1. **🚨 Pregnant animals** (highest priority)
2. **🦁 Wild temperament** (harder to catch)
3. **👥 Multiple animals** (efficiency gains)
4. **📍 Location clustering** (route optimization)

---

## 🤝 Contributing & Extending

This is designed to be **community-friendly** and **easily adaptable**:

### 🌍 **For Other Regions**:
- Fork the repository
- Update map center coordinates
- Customize data fields as needed
- Add local language support

### 💡 **Feature Ideas**:
- Veterinarian scheduling integration
- Supply/medication tracking
- Volunteer coordination tools
- Multi-language support
- Photo recognition for animal ID

### 🔧 **Technical Contributions**:
1. Fork this repository
2. Create a feature branch
3. Submit a pull request
4. Join our community discussions

---

## 📞 Support & Community

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Join community conversations in GitHub Discussions
- **Documentation**: Comprehensive guides in `/docs` folder
- **API**: RESTful endpoints for external integrations

---

## 📄 License

[MIT License](LICENSE) - Free for rescue organizations worldwide

---

## 🙏 Acknowledgments

Built by volunteers in Koh Phangan in collaboration with:
- **PACS Thailand** - Animal rescue and welfare
- **Local volunteers** - Data collection and field work
- **Open source community** - Tools and inspiration

_This project demonstrates how simple technology can create powerful tools for animal welfare. It's designed to be replicated, adapted, and improved by rescue organizations everywhere._