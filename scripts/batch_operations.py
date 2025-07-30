#!/usr/bin/env python3
"""
Batch operations script for PACS Dog Map
Allows bulk status updates and data management
"""

import pandas as pd
import sys
import argparse

def load_data():
    """Load the current CSV data"""
    try:
        return pd.read_csv("sample_data.csv")
    except FileNotFoundError:
        try:
            return pd.read_csv("PACS_Test_1_List_v2.csv")
        except FileNotFoundError:
            print("❌ No CSV file found!")
            return None

def mark_completed(animal_ids):
    """Mark specific animals as completed"""
    df = load_data()
    if df is None:
        return
    
    # Assume animal_ids are row indices
    for idx in animal_ids:
        if idx < len(df):
            df.at[idx, 'Status'] = 'Completed'
            location = df.at[idx, 'Location (Area)']
            animal = df.at[idx, 'Dog/Cat']
            print(f"✅ Marked {animal} at {location} as completed")
    
    # Save updated data
    df.to_csv("sample_data.csv", index=False)
    print(f"💾 Updated {len(animal_ids)} records")

def list_pending():
    """List all pending animals"""
    df = load_data()
    if df is None:
        return
    
    pending = df[df['Status'] != 'Completed']
    print(f"\n📋 {len(pending)} PENDING ANIMALS:\n")
    
    for idx, row in pending.iterrows():
        priority = "🚨 HIGH PRIORITY" if row.get('Pregnant?', '').lower() == 'yes' else ""
        print(f"ID {idx}: {row['Dog/Cat']} at {row['Location (Area)']} - {row['Temperament']} {priority}")
        print(f"    Contact: {row['Contact Name']} ({row.get('Contact Phone #', 'N/A')})")
        print(f"    Status: {row['Status']}\n")

def generate_priority_list():
    """Generate priority-sorted list"""
    df = load_data()
    if df is None:
        return
    
    # Priority scoring
    def priority_score(row):
        score = 0
        if row.get('Pregnant?', '').lower() == 'yes':
            score += 10  # Highest priority
        if row['Temperament'] == 'Wild':
            score += 5   # Harder to catch
        if row['Sex'] == 'Both':
            score += 3   # Multiple animals
        return score
    
    df['Priority_Score'] = df.apply(priority_score, axis=1)
    priority_list = df[df['Status'] != 'Completed'].sort_values('Priority_Score', ascending=False)
    
    print("🎯 PRIORITY ORDER FOR FIELD WORK:\n")
    for idx, row in priority_list.iterrows():
        score_text = f"Priority: {row['Priority_Score']}"
        print(f"ID {idx}: {row['Location (Area)']} - {row['Dog/Cat']} ({row['Sex']}) - {score_text}")
        if row.get('Pregnant?', '').lower() == 'yes':
            print("    🚨 PREGNANT - URGENT!")
        print(f"    Maps: {row['Location Link']}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PACS Dog Map Batch Operations")
    parser.add_argument('--complete', nargs='+', type=int, help='Mark animal IDs as completed')
    parser.add_argument('--list', action='store_true', help='List all pending animals')
    parser.add_argument('--priority', action='store_true', help='Show priority order')
    
    args = parser.parse_args()
    
    if args.complete:
        mark_completed(args.complete)
    elif args.list:
        list_pending()
    elif args.priority:
        generate_priority_list()
    else:
        print("PACS Dog Map - Batch Operations")
        print("Usage examples:")
        print("  python batch_operations.py --list")
        print("  python batch_operations.py --priority") 
        print("  python batch_operations.py --complete 0 1 2")