#!/usr/bin/env python3
"""Test script for plotting functions"""

import pandas as pd
import numpy as np
from plotting import create_correlation_heatmap, create_trends_chart, create_funnel_chart, create_box_plot, create_sunburst_chart

# Create sample data
np.random.seed(42)
n_samples = 50

sample_data = pd.DataFrame({
    'Application_ID': [f'APP-{i:03d}' for i in range(n_samples)],
    'Application_Date': pd.date_range(start='2024-01-01', periods=n_samples, freq='D'),
    'Age': np.random.randint(25, 65, n_samples),
    'Gender': np.random.choice(['Male', 'Female'], n_samples),
    'Monthly_Income': np.random.randint(25000, 80000, n_samples),
    'Credit_Score': np.random.randint(550, 850, n_samples),
    'DTI_Ratio': np.random.uniform(0.1, 0.6, n_samples),
    'Employment_Status': np.random.choice(['Employed', 'Self-Employed', 'Unemployed'], n_samples),
    'Processing_Time_Days': np.random.randint(1, 45, n_samples),
    'Status': np.random.choice(['Approved', 'Declined', 'In-Process', 'Withdrawn'], n_samples)
})

print("Testing plotting functions...")

try:
    print("1. Testing correlation heatmap...")
    fig1 = create_correlation_heatmap(sample_data)
    print("   ✓ Correlation heatmap created successfully")
except Exception as e:
    print(f"   ✗ Error in correlation heatmap: {e}")

try:
    print("2. Testing trends chart...")
    fig2 = create_trends_chart(sample_data)
    print("   ✓ Trends chart created successfully")
except Exception as e:
    print(f"   ✗ Error in trends chart: {e}")

try:
    print("3. Testing funnel chart...")
    fig3 = create_funnel_chart(sample_data)
    print("   ✓ Funnel chart created successfully")
except Exception as e:
    print(f"   ✗ Error in funnel chart: {e}")

try:
    print("4. Testing box plot...")
    fig4 = create_box_plot(sample_data)
    print("   ✓ Box plot created successfully")
except Exception as e:
    print(f"   ✗ Error in box plot: {e}")

try:
    print("5. Testing sunburst chart...")
    fig5 = create_sunburst_chart(sample_data)
    print("   ✓ Sunburst chart created successfully")
except Exception as e:
    print(f"   ✗ Error in sunburst chart: {e}")

print("\nAll tests completed!")

# Test edge cases
print("\nTesting edge cases...")

# Empty dataframe
empty_df = pd.DataFrame()
try:
    fig_empty = create_correlation_heatmap(empty_df)
    print("✓ Empty dataframe handled correctly for correlation heatmap")
except Exception as e:
    print(f"✗ Error with empty dataframe: {e}")

# Dataframe with insufficient numeric columns
minimal_df = pd.DataFrame({'Status': ['Approved', 'Declined']})
try:
    fig_minimal = create_correlation_heatmap(minimal_df)
    print("✓ Minimal dataframe handled correctly for correlation heatmap")
except Exception as e:
    print(f"✗ Error with minimal dataframe: {e}")

print("Edge case tests completed!")