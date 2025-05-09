# COVID-19 Global Trends Analysis
# Complete Data Analysis and Reporting Script

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime
from IPython.display import display, Markdown
import warnings
warnings.filterwarnings('ignore')


# 1. DATA LOADING


def load_data():
    """Load COVID-19 dataset from Our World in Data"""
    print("🔍 Loading COVID-19 dataset...")
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
    df = pd.read_csv(url, parse_dates=['date'])
    
    # Basic dataset info
    print(f"\n✅ Dataset loaded successfully (shape: {df.shape})")
    print(f"📅 Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"🌍 Countries/regions: {df['location'].nunique()}")
    
    return df


# 2. DATA CLEANING


def clean_data(df, countries=None):
    """Clean and preprocess COVID-19 data"""
    print("\n🧹 Cleaning data...")
    
    # Select columns of interest
    cols = [
        'date', 'location', 'continent', 'population',
        'total_cases', 'new_cases', 'total_deaths', 'new_deaths',
        'total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated'
    ]
    df = df[cols].copy()
    
    # Filter specific countries if provided
    if countries:
        df = df[df['location'].isin(countries)]
    
    # Forward fill missing values within each country
    df_clean = df.groupby('location').apply(lambda x: x.ffill())
    
    # Calculate additional metrics
    df_clean['cases_per_million'] = (df_clean['total_cases'] / df_clean['population']) * 1e6
    df_clean['deaths_per_million'] = (df_clean['total_deaths'] / df_clean['population']) * 1e6
    df_clean['mortality_rate'] = df_clean['total_deaths'] / df_clean['total_cases']
    df_clean['vaccination_rate'] = df_clean['people_vaccinated'] / df_clean['population']
    
    # Drop rows with missing values in key metrics
    df_clean = df_clean.dropna(subset=['cases_per_million', 'deaths_per_million'])
    
    print("✅ Data cleaning complete!")
    return df_clean

# 3. EXPLORATORY ANALYSIS


def plot_time_series(df, metric, title, save_path=None):
    """Plot time series for specified metric and save the plot if save_path is provided"""
    plt.figure(figsize=(14, 7))
    sns.lineplot(data=df, x='date', y=metric, hue='location')
    plt.title(title, fontsize=16)
    plt.ylabel(metric.replace('_', ' ').title(), fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.legend(title='Country')
    plt.grid(True)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')  # Save the plot
        print(f"💾 Plot saved to {save_path}")
    
    plt.show()

def plot_comparison(df, metric, title, save_path=None):
    """Plot comparison of latest values across countries"""
    latest = df[df['date'] == df['date'].max()]
    plt.figure(figsize=(12, 6))
    sns.barplot(data=latest.sort_values(metric, ascending=False), 
                x='location', y=metric)
    plt.title(title, fontsize=16)
    plt.ylabel(metric.replace('_', ' ').title(), fontsize=12)
    plt.xlabel('Country', fontsize=12)
    plt.xticks(rotation=45)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')  # Save the plot
        print(f"💾 Plot saved to {save_path}")
    
    plt.show()

# 4. INTERACTIVE VISUALIZATIONS


def create_interactive_map(df, metric, title, save_path=None):
    """Create choropleth map for specified metric"""
    latest = df[df['date'] == df['date'].max()]
    
    # Debugging: Check the data
    print(f"Latest DataFrame shape: {latest.shape}")
    print(latest[[metric, 'location']].head())  # Check the metric column and location
    
    fig = px.choropleth(
        latest,
        locations="location",
        locationmode="country names",
        color=metric,
        hover_name="location",
        color_continuous_scale="Viridis",
        title=title
    )
    fig.show()

def create_vaccination_dashboard(df):
    """Interactive vaccination progress dashboard"""
    vacc_df = df[df['date'] >= '2021-01-01']  # Vaccinations started around here
    
    fig = px.line(vacc_df, 
                 x='date', 
                 y='vaccination_rate',
                 color='location',
                 title='COVID-19 Vaccination Progress',
                 labels={'vaccination_rate': 'Vaccination Rate'})
    fig.show()


# 5. INSIGHT GENERATION


def generate_insights(df, save_path=None):
    """Generate key insights from the data and optionally save them to a file"""
    latest = df[df['date'] == df['date'].max()]
    
    # Top countries analysis
    top_cases = latest.nlargest(3, 'total_cases')['location'].tolist()
    top_deaths = latest.nlargest(3, 'total_deaths')['location'].tolist()
    top_vaccinated = latest.nlargest(3, 'vaccination_rate')['location'].tolist()
    
    # Mortality analysis
    high_mortality = latest[latest['total_cases'] > 1e6].nlargest(3, 'mortality_rate')
    
    # Prepare insights
    insights = []
    insights.append("\n🔎 KEY INSIGHTS:")
    insights.append(f"1. Countries with most cases: {', '.join(top_cases)}")
    insights.append(f"2. Countries with most deaths: {', '.join(top_deaths)}")
    insights.append(f"3. Countries with highest vaccination rates: {', '.join(top_vaccinated)}")
    insights.append("\n4. Highest mortality rates among major countries:")
    for _, row in high_mortality.iterrows():
        insights.append(f"   - {row['location']}: {row['mortality_rate']:.2%}")
    
    # Print insights to console
    for line in insights:
        print(line)
    
    # Save insights to a file if a save path is provided
    if save_path:
        with open(save_path, 'w') as file:
            file.write('\n'.join(insights))
        print(f"\n💾 Insights saved to '{save_path}'")


# 6. MAIN EXECUTION


def main():
    # Load data
    df = load_data()
    
    # Select countries for analysis (can be customized)
    countries = ['United States', 'India', 'Brazil', 'United Kingdom', 'Germany', 'Japan', 'Kenya']
    df_clean = clean_data(df, countries)
    
    # Time series analysis
    print("\n📈 TIME SERIES ANALYSIS")
    plot_time_series(df_clean, 'total_cases', 'Total COVID-19 Cases Over Time', save_path='total_cases_over_time.png')
    plot_time_series(df_clean, 'new_cases', 'Daily New COVID-19 Cases (7-day avg)', save_path='daily_new_cases.png')
    
    # Comparative analysis
    print("\n📊 COMPARATIVE ANALYSIS")
    plot_comparison(df_clean, 'cases_per_million', 'Cases per Million Population', save_path='cases_per_million.png')
    plot_comparison(df_clean, 'deaths_per_million', 'Deaths per Million Population', save_path='deaths_per_million.png')
    
    # Interactive visualizations
    print("\n🌍 INTERACTIVE VISUALIZATIONS")
    create_interactive_map(df_clean, 'cases_per_million', 'Global COVID-19 Cases per Million', save_path='cases_per_million_map.html')
    create_interactive_map(df_clean, 'deaths_per_million', 'Global COVID-19 Deaths per Million', save_path='deaths_per_million_map.html')
    
    # Generate insights and save them to a file
    generate_insights(df_clean, save_path='insights.txt')
    
    # Save cleaned data
    df_clean.to_csv('covid_analysis_results.csv', index=False)
    print("\n💾 Analysis results saved to 'covid_analysis_results.csv'")

if __name__ == "__main__":
    main()