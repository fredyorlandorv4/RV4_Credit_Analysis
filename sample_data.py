# sample_data.py - Enhanced version with realistic financial calculations and training data
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import random

def calculate_monthly_payment(loan_amount, interest_rate, loan_duration_years):
    """Calculate monthly payment using mortgage formula"""
    if interest_rate > 0 and loan_duration_years > 0:
        monthly_rate = interest_rate / 100 / 12
        n_payments = loan_duration_years * 12
        if monthly_rate > 0:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** n_payments) / \
                            ((1 + monthly_rate) ** n_payments - 1)
        else:
            monthly_payment = loan_amount / n_payments
    else:
        monthly_payment = loan_amount / (loan_duration_years * 12) if loan_duration_years > 0 else 0
    
    return monthly_payment

def calculate_dti(monthly_payment, monthly_income):
    """Calculate debt-to-income ratio"""
    if monthly_income > 0:
        return monthly_payment / monthly_income
    return 0

def get_realistic_interest_rate(credit_score, loan_duration, base_rate=7.5):
    """Calculate realistic interest rate based on credit score and loan term"""
    # Base Guatemala mortgage rates around 7.5%
    rate = base_rate
    
    # Credit score adjustment
    if credit_score >= 750:
        rate -= 1.0  # Best rates
    elif credit_score >= 700:
        rate -= 0.5
    elif credit_score >= 650:
        rate += 0.0  # Standard rate
    elif credit_score >= 600:
        rate += 0.5
    elif credit_score >= 550:
        rate += 1.0
    else:
        rate += 2.0  # Higher risk rate
    
    # Loan duration adjustment (longer terms = higher rates)
    if loan_duration >= 25:
        rate += 0.5
    elif loan_duration >= 20:
        rate += 0.3
    
    # Add some random variation
    rate += np.random.uniform(-0.3, 0.3)
    
    return max(5.5, min(12.0, rate))  # Cap between 5.5% and 12%

def determine_approval_based_on_factors(credit_score, dti_ratio, ltv_ratio, employment_duration, monthly_income):
    """Determine approval probability based on realistic lending criteria"""
    score = 0
    
    # Credit Score (40% weight)
    if credit_score >= 720:
        score += 40
    elif credit_score >= 680:
        score += 35
    elif credit_score >= 640:
        score += 25
    elif credit_score >= 600:
        score += 15
    elif credit_score >= 550:
        score += 5
    else:
        score += 0
    
    # DTI Ratio (30% weight)
    if dti_ratio <= 0.28:
        score += 30
    elif dti_ratio <= 0.36:
        score += 25
    elif dti_ratio <= 0.43:
        score += 15
    elif dti_ratio <= 0.50:
        score += 5
    else:
        score += 0
    
    # LTV Ratio (20% weight)
    if ltv_ratio <= 80:
        score += 20
    elif ltv_ratio <= 85:
        score += 15
    elif ltv_ratio <= 90:
        score += 10
    elif ltv_ratio <= 95:
        score += 5
    else:
        score += 0
    
    # Employment Duration (5% weight)
    if employment_duration >= 24:
        score += 5
    elif employment_duration >= 12:
        score += 3
    elif employment_duration >= 6:
        score += 1
    
    # Income level (5% weight)
    if monthly_income >= 60000:
        score += 5
    elif monthly_income >= 40000:
        score += 3
    elif monthly_income >= 25000:
        score += 1
    
    # Add randomness to avoid perfect predictions - increase variability
    score += np.random.uniform(-15, 15)  # Increased from -10,10 to -15,15
    
    # Add some edge cases that don't follow the rules (10% of cases)
    if np.random.random() < 0.1:
        score += np.random.uniform(-20, 20)  # Extra randomness for edge cases
    
    return max(0, min(100, score))

def generate_realistic_application(index, force_status=None):
    """Generate a single realistic application with proper financial calculations"""
    
    # Start with realistic demographics
    age = np.random.randint(25, 65)
    gender = np.random.choice(['Male', 'Female'], p=[0.55, 0.45])
    marital_status = np.random.choice(['Single', 'Married', 'Divorced', 'Widowed'], 
                                     p=[0.3, 0.5, 0.15, 0.05])
    
    # Employment - realistic distribution
    employment_status = np.random.choice(['Employed', 'Self-Employed'], p=[0.8, 0.2])
    employment_duration = max(0, int(np.random.normal(36, 24)))  # Average 3 years, some variation
    
    # Income - realistic distribution (Guatemala salary ranges)
    if employment_status == 'Employed':
        # Employees have more stable income distribution
        monthly_income = max(15000, np.random.lognormal(10.5, 0.6))  # Log-normal distribution
    else:
        # Self-employed have more variable income
        monthly_income = max(12000, np.random.lognormal(10.3, 0.8))
    
    monthly_income = min(monthly_income, 200000)  # Cap at reasonable max
    
    # Credit Score - realistic distribution
    credit_score = int(np.random.normal(650, 80))
    credit_score = max(300, min(850, credit_score))
    
    # Property and loan details - start with realistic constraints
    # Property price based on income (typically 3-5x annual income in Guatemala)
    annual_income = monthly_income * 12
    property_price_multiplier = np.random.uniform(2.5, 6.0)
    property_price = annual_income * property_price_multiplier
    property_price = round(property_price / 10000) * 10000  # Round to nearest 10k
    
    # Down payment - realistic range (10-30% in Guatemala)
    down_payment_percentage = np.random.uniform(0.10, 0.30)
    if credit_score >= 700:
        down_payment_percentage = np.random.uniform(0.15, 0.25)  # Better credit = lower down payment
    
    down_payment = property_price * down_payment_percentage
    loan_amount = property_price - down_payment
    
    # Loan duration - realistic distribution
    loan_duration = np.random.choice([15, 20, 25, 30], p=[0.2, 0.4, 0.3, 0.1])
    
    # Interest rate based on credit score and loan term
    interest_rate = get_realistic_interest_rate(credit_score, loan_duration)
    
    # Calculate actual monthly payment
    monthly_payment = calculate_monthly_payment(loan_amount, interest_rate, loan_duration)
    
    # Calculate actual DTI
    dti_ratio = calculate_dti(monthly_payment, monthly_income)
    
    # Calculate LTV
    ltv_ratio = (loan_amount / property_price) * 100
    
    # Determine approval probability based on realistic factors
    approval_score = determine_approval_based_on_factors(
        credit_score, dti_ratio, ltv_ratio, employment_duration, monthly_income
    )
    
    # Determine status based on approval score and add MORE realistic randomness
    if force_status:
        status = force_status
    else:
        # More realistic and variable approval thresholds
        random_factor = np.random.uniform(0, 1)
        
        # Add market conditions randomness (sometimes good applicants get declined due to external factors)
        market_factor = np.random.uniform(-10, 10)  # Market conditions affect decisions
        adjusted_score = approval_score + market_factor
        
        if adjusted_score >= 80:
            # High score but still some variation
            status = np.random.choice(['Approved', 'In-Process'], p=[0.85, 0.15])
        elif adjusted_score >= 65:
            # Good score with more variation
            status = np.random.choice(['Approved', 'In-Process', 'Withdrawn'], p=[0.6, 0.35, 0.05])
        elif adjusted_score >= 45:
            # Medium score - most unpredictable
            status = np.random.choice(['Approved', 'In-Process', 'Declined', 'Withdrawn'], p=[0.25, 0.4, 0.25, 0.1])
        elif adjusted_score >= 25:
            # Lower score but still some approvals
            status = np.random.choice(['Declined', 'In-Process', 'Withdrawn', 'Approved'], p=[0.5, 0.3, 0.15, 0.05])
        else:
            # Very low score but real world has exceptions
            status = np.random.choice(['Declined', 'Withdrawn', 'In-Process'], p=[0.7, 0.25, 0.05])
    
    # Processing details with more realistic variation (less correlated with status)
    base_variation = np.random.uniform(0.8, 1.2)  # General variation factor
    
    if status == 'Approved':
        processing_days = max(5, int(np.random.normal(25, 8) * base_variation))
        documents_submitted = np.random.randint(3, 6)  # Some approved with fewer docs
        completeness_score = max(50, np.random.normal(85, 10) * base_variation)
        communication_frequency = max(0.5, np.random.normal(2.0, 0.5) * base_variation)
        withdrawal_risk = max(5, np.random.normal(15, 8) * base_variation)
    elif status == 'Declined':
        processing_days = max(3, int(np.random.normal(18, 7) * base_variation))
        documents_submitted = np.random.randint(1, 5)  # Some declined have many docs
        completeness_score = max(20, np.random.normal(55, 15) * base_variation)
        communication_frequency = max(0.1, np.random.normal(1.0, 0.4) * base_variation)
        withdrawal_risk = max(10, np.random.normal(30, 12) * base_variation)
    elif status == 'Withdrawn':
        processing_days = max(5, int(np.random.normal(35, 15) * base_variation))
        documents_submitted = np.random.randint(1, 5)
        completeness_score = max(15, np.random.normal(60, 20) * base_variation)
        communication_frequency = max(0.1, np.random.normal(0.8, 0.4) * base_variation)
        withdrawal_risk = max(50, np.random.normal(80, 10) * base_variation)
    else:  # In-Process
        processing_days = max(1, int(np.random.normal(15, 8) * base_variation))
        documents_submitted = np.random.randint(2, 6)  # Wide range for in-process
        completeness_score = max(30, np.random.normal(75, 15) * base_variation)
        communication_frequency = max(0.2, np.random.normal(1.5, 0.6) * base_variation)
        withdrawal_risk = max(10, np.random.normal(40, 20) * base_variation)
    
    # Cap values at reasonable limits
    completeness_score = min(100, max(0, completeness_score))
    communication_frequency = min(5.0, max(0.1, communication_frequency))
    withdrawal_risk = min(95, max(5, withdrawal_risk))
    
    # Generate application date
    if status in ['Approved', 'Declined']:
        days_ago = np.random.randint(30, 365)
    elif status == 'Withdrawn':
        days_ago = np.random.randint(20, 180)
    else:  # In-Process
        days_ago = np.random.randint(0, 30)
    
    application_date = datetime.now() - timedelta(days=days_ago)
    
    # Client information
    first_names = ['Juan', 'Maria', 'Carlos', 'Ana', 'Luis', 'Carmen', 'Jose', 'Rosa', 
                   'Pedro', 'Isabel', 'Miguel', 'Sofia', 'Jorge', 'Elena', 'Roberto']
    last_names = ['Garcia', 'Rodriguez', 'Martinez', 'Lopez', 'Gonzalez', 'Perez', 
                  'Sanchez', 'Ramirez', 'Torres', 'Flores', 'Rivera', 'Gomez']
    
    first_name = np.random.choice(first_names)
    last_name = np.random.choice(last_names)
    client_name = f"{first_name} {last_name}"
    
    # Generate DPI (Guatemala's personal identification)
    dpi = f"{np.random.randint(1000, 9999)} {np.random.randint(10000, 99999)} {np.random.randint(1000, 9999)}"
    
    # Email
    email = f"{first_name.lower()}.{last_name.lower()}@example.com"
    
    # Phone (Guatemala format)
    phone = f"+502 {np.random.randint(3000, 7999)}-{np.random.randint(1000, 9999)}"
    
    # Address
    zones = ['Zona 1', 'Zona 10', 'Zona 14', 'Zona 15', 'Zona 16']
    cities = ['Guatemala City', 'Quetzaltenango', 'Escuintla', 'Antigua Guatemala']
    address = f"{np.random.randint(1, 99)} Calle {np.random.randint(1, 30)}-{np.random.randint(1, 99)}, {np.random.choice(zones)}, {np.random.choice(cities)}"
    
    # Application and product types
    application_type = np.random.choice(['New Mortgage', 'Refinance', 'Home Equity'], 
                                       p=[0.6, 0.3, 0.1])
    product_type = 'Mortgage'
    
    # Loan decision
    loan_decision = status if status in ['Approved', 'Declined'] else None
    
    return {
        # Identifiers
        'Application_ID': f'RV4-2024{str(index).zfill(6)}',
        'application_id': f'RV4-2024{str(index).zfill(6)}',
        'Application_Date': application_date,
        
        # Client Information
        'client_name': client_name,
        'dpi': dpi,
        'email': email,
        'phone': phone,
        'address': address,
        
        # Personal Demographics
        'Age': age,
        'age': age,
        'Gender': gender,
        'gender': gender,
        'marital_status': marital_status,
        
        # Employment & Financial
        'Employment_Status': employment_status,
        'employment_status': employment_status,
        'Employment_Duration_Months': employment_duration,
        'employment_duration_months': employment_duration,
        'Monthly_Income': round(monthly_income, 2),
        'monthly_income': round(monthly_income, 2),
        'Credit_Score': credit_score,
        'credit_score': credit_score,
        'DTI_Ratio': round(dti_ratio, 4),
        'dti_ratio': round(dti_ratio, 4),
        
        # Loan Details
        'application_type': application_type,
        'product_type': product_type,
        'Loan_Amount': round(loan_amount, 2),
        'loan_amount': round(loan_amount, 2),
        'Property_Price': round(property_price, 2),
        'property_price': round(property_price, 2),
        'Down_Payment': round(down_payment, 2),
        'down_payment': round(down_payment, 2),
        'Interest_Rate': round(interest_rate, 2),
        'interest_rate': round(interest_rate, 2),
        'Loan_Duration': loan_duration,
        'loan_duration': loan_duration,
        'Monthly_Payment': round(monthly_payment, 2),
        'monthly_payment': round(monthly_payment, 2),
        
        # Processing Information
        'Status': status,
        'status': status,
        'loan_decision': loan_decision,
        'Processing_Time_Days': processing_days,
        'processing_time_days': processing_days,
        'Days_In_Process': processing_days,
        'Documents_Submitted': documents_submitted,
        'documents_submitted': documents_submitted,
        'completeness_score': round(completeness_score, 1),
        'Communication_Frequency': round(communication_frequency, 2),
        'communication_frequency': round(communication_frequency, 2),
        
        # ML Predictions (based on calculated factors)
        'approval_probability': round(approval_score, 2),
        'withdrawal_risk': round(withdrawal_risk, 2),
        
        # Additional fields for compatibility
        'notes': None,
        'last_contact_date': application_date + timedelta(days=np.random.randint(1, max(2, processing_days + 1))) if processing_days > 0 else None,
        
        # Calculate LTV for reference
        'ltv_ratio': round(ltv_ratio, 2)
    }

def generate_and_save_data(output_path='data/credit_data.csv', num_records=565):
    """Generate and save comprehensive sample dataset with realistic financial relationships"""
    if os.path.exists(output_path):
        print(f"'{output_path}' already exists. Skipping generation.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Generate all records with natural distribution
    all_records = []
    
    # Generate records without forcing status - let them distribute naturally
    for i in range(1, num_records + 1):
        record = generate_realistic_application(i)
        all_records.append(record)
    
    # Shuffle to mix any patterns
    np.random.shuffle(all_records)
    
    # Create DataFrame
    df = pd.DataFrame(all_records)
    
    # Sort by application date (most recent first)
    df = df.sort_values('Application_Date', ascending=False)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    
    # Print statistics
    print(f"Sample data generated and saved to '{output_path}'.")
    print(f"Total records: {len(df)}")
    print(f"\nStatus distribution:")
    print(df['Status'].value_counts())
    print(f"\nDTI Ratio summary:")
    print(f"  Mean: {df['DTI_Ratio'].mean():.3f}")
    print(f"  Median: {df['DTI_Ratio'].median():.3f}")
    print(f"  Min: {df['DTI_Ratio'].min():.3f}")
    print(f"  Max: {df['DTI_Ratio'].max():.3f}")
    print(f"\nCredit Score summary:")
    print(f"  Mean: {df['Credit_Score'].mean():.0f}")
    print(f"  Median: {df['Credit_Score'].median():.0f}")
    print(f"  Min: {df['Credit_Score'].min()}")
    print(f"  Max: {df['Credit_Score'].max()}")
    print(f"\nLTV Ratio summary:")
    print(f"  Mean: {df['ltv_ratio'].mean():.1f}%")
    print(f"  Median: {df['ltv_ratio'].median():.1f}%")
    print(f"  Min: {df['ltv_ratio'].min():.1f}%")
    print(f"  Max: {df['ltv_ratio'].max():.1f}%")
    print(f"\nInterest Rate summary:")
    print(f"  Mean: {df['Interest_Rate'].mean():.2f}%")
    print(f"  Median: {df['Interest_Rate'].median():.2f}%")
    print(f"  Min: {df['Interest_Rate'].min():.2f}%")
    print(f"  Max: {df['Interest_Rate'].max():.2f}%")
    
    # Show correlation between approval and key factors
    approved = df[df['Status'] == 'Approved']
    declined = df[df['Status'] == 'Declined']
    
    if len(approved) > 0 and len(declined) > 0:
        print(f"\nApproved vs Declined comparison:")
        print(f"  Avg Credit Score - Approved: {approved['Credit_Score'].mean():.0f}, Declined: {declined['Credit_Score'].mean():.0f}")
        print(f"  Avg DTI Ratio - Approved: {approved['DTI_Ratio'].mean():.3f}, Declined: {declined['DTI_Ratio'].mean():.3f}")
        print(f"  Avg LTV Ratio - Approved: {approved['ltv_ratio'].mean():.1f}%, Declined: {declined['ltv_ratio'].mean():.1f}%")

if __name__ == '__main__':
    generate_and_save_data()