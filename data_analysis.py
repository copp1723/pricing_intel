#!/usr/bin/env python3
"""
Comprehensive Data Analysis for Pricing Intelligence Platform
Analyzes the inventory CSV data to understand structure, quality, and requirements.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime

def analyze_csv_data(csv_path):
    """Perform comprehensive analysis of the inventory CSV data"""
    
    print("=" * 80)
    print("PRICING INTELLIGENCE PLATFORM - DATA ANALYSIS")
    print("=" * 80)
    
    # Load the data
    print(f"\n1. Loading data from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    print(f"   - Total records: {len(df)}")
    print(f"   - Total columns: {len(df.columns)}")
    
    # Basic data info
    print(f"\n2. DATA STRUCTURE")
    print(f"   - Shape: {df.shape}")
    print(f"   - Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    # Column analysis
    print(f"\n3. COLUMN ANALYSIS")
    print(f"   Columns ({len(df.columns)}):")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i:2d}. {col}")
    
    # Data types
    print(f"\n4. DATA TYPES")
    for col in df.columns:
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        null_pct = (null_count / len(df)) * 100
        unique_count = df[col].nunique()
        print(f"   {col:20s} | {str(dtype):10s} | Nulls: {null_count:4d} ({null_pct:5.1f}%) | Unique: {unique_count:5d}")
    
    # Key field analysis
    print(f"\n5. KEY FIELD ANALYSIS")
    
    # VIN analysis
    print(f"\n   VIN Analysis:")
    vin_stats = df['VIN'].describe()
    print(f"   - Total VINs: {len(df['VIN'])}")
    print(f"   - Unique VINs: {df['VIN'].nunique()}")
    print(f"   - Duplicate VINs: {len(df) - df['VIN'].nunique()}")
    if df['VIN'].nunique() != len(df):
        duplicates = df[df.duplicated('VIN', keep=False)]['VIN'].value_counts()
        print(f"   - Top duplicate VINs: {duplicates.head()}")
    
    # Price analysis
    print(f"\n   Price Analysis:")
    price_stats = df['Price'].describe()
    print(f"   - Min price: ${price_stats['min']:,.2f}")
    print(f"   - Max price: ${price_stats['max']:,.2f}")
    print(f"   - Mean price: ${price_stats['mean']:,.2f}")
    print(f"   - Median price: ${price_stats['50%']:,.2f}")
    
    # Year analysis
    print(f"\n   Year Analysis:")
    year_counts = df['Year'].value_counts().sort_index()
    print(f"   - Year range: {df['Year'].min()} - {df['Year'].max()}")
    print(f"   - Most common years:")
    for year, count in year_counts.tail(5).items():
        print(f"     {year}: {count} vehicles")
    
    # Make/Model analysis
    print(f"\n   Make/Model Analysis:")
    make_counts = df['Make'].value_counts()
    print(f"   - Unique makes: {df['Make'].nunique()}")
    print(f"   - Top makes:")
    for make, count in make_counts.head(5).items():
        print(f"     {make}: {count} vehicles")
    
    model_counts = df['Model'].value_counts()
    print(f"   - Unique models: {df['Model'].nunique()}")
    print(f"   - Top models:")
    for model, count in model_counts.head(5).items():
        print(f"     {model}: {count} vehicles")
    
    # Condition analysis
    print(f"\n   Condition Analysis:")
    condition_counts = df['Condition'].value_counts()
    for condition, count in condition_counts.items():
        pct = (count / len(df)) * 100
        print(f"   - {condition}: {count} vehicles ({pct:.1f}%)")
    
    # Mileage analysis
    print(f"\n   Mileage Analysis:")
    mileage_stats = df['Mileage'].describe()
    print(f"   - Min mileage: {mileage_stats['min']:,.0f}")
    print(f"   - Max mileage: {mileage_stats['max']:,.0f}")
    print(f"   - Mean mileage: {mileage_stats['mean']:,.0f}")
    print(f"   - Median mileage: {mileage_stats['50%']:,.0f}")
    
    # Data quality issues
    print(f"\n6. DATA QUALITY ASSESSMENT")
    
    # Missing values
    print(f"\n   Missing Values:")
    missing_data = df.isnull().sum()
    missing_pct = (missing_data / len(df)) * 100
    for col in missing_data[missing_data > 0].index:
        print(f"   - {col}: {missing_data[col]} ({missing_pct[col]:.1f}%)")
    
    # Potential issues
    print(f"\n   Potential Data Issues:")
    
    # Price issues
    zero_prices = (df['Price'] == 0).sum()
    if zero_prices > 0:
        print(f"   - Zero prices: {zero_prices} records")
    
    # Mileage issues
    zero_mileage = (df['Mileage'] == 0).sum()
    if zero_mileage > 0:
        print(f"   - Zero mileage: {zero_mileage} records (likely new vehicles)")
    
    # VIN format issues
    invalid_vins = df[df['VIN'].str.len() != 17]['VIN'].count()
    if invalid_vins > 0:
        print(f"   - Invalid VIN length: {invalid_vins} records")
    
    # Requirements for matching engine
    print(f"\n7. MATCHING ENGINE REQUIREMENTS")
    print(f"   Key fields for vehicle matching:")
    print(f"   - Year: Required for age-based matching")
    print(f"   - Make: Required for brand matching") 
    print(f"   - Model: Required for model matching")
    print(f"   - Trim: Available for precise matching")
    print(f"   - Mileage: Available for condition matching")
    print(f"   - Condition: Available (New/Certified/Used)")
    print(f"   - VIN: Unique identifier for exact matching")
    
    # Generate summary statistics
    summary = {
        'total_records': len(df),
        'total_columns': len(df.columns),
        'unique_vins': df['VIN'].nunique(),
        'duplicate_vins': len(df) - df['VIN'].nunique(),
        'price_range': {
            'min': float(df['Price'].min()),
            'max': float(df['Price'].max()),
            'mean': float(df['Price'].mean()),
            'median': float(df['Price'].median())
        },
        'year_range': {
            'min': int(df['Year'].min()),
            'max': int(df['Year'].max())
        },
        'unique_makes': df['Make'].nunique(),
        'unique_models': df['Model'].nunique(),
        'condition_distribution': df['Condition'].value_counts().to_dict(),
        'missing_data_summary': missing_data[missing_data > 0].to_dict(),
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    return df, summary

def create_visualizations(df, output_dir):
    """Create data visualization charts"""
    
    print(f"\n8. CREATING VISUALIZATIONS")
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create output directory
    viz_dir = Path(output_dir) / 'visualizations'
    viz_dir.mkdir(exist_ok=True)
    
    # 1. Price distribution
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.hist(df['Price'], bins=50, alpha=0.7, edgecolor='black')
    plt.title('Price Distribution')
    plt.xlabel('Price ($)')
    plt.ylabel('Frequency')
    plt.ticklabel_format(style='plain', axis='x')
    
    plt.subplot(1, 2, 2)
    plt.boxplot(df['Price'])
    plt.title('Price Box Plot')
    plt.ylabel('Price ($)')
    plt.ticklabel_format(style='plain', axis='y')
    
    plt.tight_layout()
    plt.savefig(viz_dir / 'price_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Year distribution
    plt.figure(figsize=(12, 6))
    year_counts = df['Year'].value_counts().sort_index()
    plt.bar(year_counts.index, year_counts.values, alpha=0.7, edgecolor='black')
    plt.title('Vehicle Year Distribution')
    plt.xlabel('Year')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(viz_dir / 'year_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Make distribution
    plt.figure(figsize=(12, 8))
    make_counts = df['Make'].value_counts().head(10)
    plt.barh(range(len(make_counts)), make_counts.values, alpha=0.7)
    plt.yticks(range(len(make_counts)), make_counts.index)
    plt.title('Top 10 Vehicle Makes')
    plt.xlabel('Count')
    plt.tight_layout()
    plt.savefig(viz_dir / 'make_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Price vs Mileage scatter plot
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(df['Mileage'], df['Price'], alpha=0.6, c=df['Year'], cmap='viridis')
    plt.colorbar(scatter, label='Year')
    plt.title('Price vs Mileage (colored by Year)')
    plt.xlabel('Mileage')
    plt.ylabel('Price ($)')
    plt.ticklabel_format(style='plain', axis='both')
    plt.tight_layout()
    plt.savefig(viz_dir / 'price_vs_mileage.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 5. Condition distribution
    plt.figure(figsize=(10, 6))
    condition_counts = df['Condition'].value_counts()
    plt.pie(condition_counts.values, labels=condition_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title('Vehicle Condition Distribution')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(viz_dir / 'condition_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   - Visualizations saved to: {viz_dir}")
    return viz_dir

def main():
    """Main analysis function"""
    
    # Set up paths
    project_root = Path(__file__).parent.parent
    data_path = project_root / 'data' / 'sample_inventory.csv'
    output_dir = project_root / 'data'
    
    # Perform analysis
    df, summary = analyze_csv_data(data_path)
    
    # Create visualizations
    viz_dir = create_visualizations(df, output_dir)
    
    # Save summary to JSON
    summary_path = output_dir / 'data_analysis_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n9. ANALYSIS COMPLETE")
    print(f"   - Summary saved to: {summary_path}")
    print(f"   - Visualizations saved to: {viz_dir}")
    
    # Recommendations
    print(f"\n10. RECOMMENDATIONS FOR SYSTEM DESIGN")
    print(f"   - Implement VIN validation and normalization")
    print(f"   - Create robust price validation (handle $0 prices)")
    print(f"   - Design flexible matching algorithm for Make/Model/Year/Trim")
    print(f"   - Consider mileage and condition in similarity scoring")
    print(f"   - Plan for handling missing data gracefully")
    print(f"   - Implement data quality monitoring and alerts")
    
    return df, summary

if __name__ == "__main__":
    main()

