import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import numpy as np


def fetch_weather_data(city, api_key):
    """
    Fetch weather data for a given city from the OpenWeatherMap API and save it to a CSV file.
    """
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        # Extract relevant information from the API response
        weather_data = {
            "date": [],
            "temperature": [],
            "humidity": [],
            "weather": []
        }
        for entry in data["list"]:
            weather_data["date"].append(entry["dt_txt"])
            weather_data["temperature"].append(entry["main"]["temp"])
            weather_data["humidity"].append(entry["main"]["humidity"])
            weather_data["weather"].append(entry["weather"][0]["description"])

        # Save the data to a CSV file
        df = pd.DataFrame(weather_data)
        df.to_csv("weather_data.csv", index=False)
        print("Weather data saved to weather_data.csv")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        exit()


def analyze_data(df):
    """
    Provide summary statistics and insights about the weather data.
    """
    print("\n--- Summary Statistics ---")
    print(df.describe())
    
    avg_temp = df["temperature"].mean()
    avg_humidity = df["humidity"].mean()
    print(f"\nAverage Temperature: {avg_temp:.2f}°C")
    print(f"Average Humidity: {avg_humidity:.2f}%")
    
    print("\n--- Weather Condition Frequency ---")
    print(df['weather'].value_counts())


def calculate_rolling_stats(df, window=3):
    """
    Calculate rolling mean and standard deviation for temperatures and identify outliers.
    """
    df['rolling_mean'] = df['temperature'].rolling(window=window).mean()
    df['rolling_std'] = df['temperature'].rolling(window=window).std()
    df['is_outlier'] = np.abs(df['temperature'] - df['rolling_mean']) > 2 * df['rolling_std']
    return df


def plot_rolling_stats(df):
    """
    Plot rolling mean, rolling standard deviation, and highlight outliers.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['temperature'], label='Temperature', color='blue', alpha=0.7)
    plt.plot(df['date'], df['rolling_mean'], label='Rolling Mean', linestyle='--', color='green')
    plt.fill_between(
        df['date'],
        df['rolling_mean'] - 2 * df['rolling_std'],
        df['rolling_mean'] + 2 * df['rolling_std'],
        color='gray',
        alpha=0.3,
        label='±2 Std Dev'
    )
    outliers = df[df['is_outlier']]
    plt.scatter(outliers['date'], outliers['temperature'], color='red', label='Outliers', zorder=5)
    
    plt.xticks(rotation=45)
    plt.title('Temperature with Rolling Statistics and Outliers')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.legend()
    plt.tight_layout()
    plt.show()

    if not outliers.empty:
        print("\nUnusually High or Low Temperatures Detected:")
        print(outliers[['date', 'temperature']])
    else:
        print("\nNo unusual temperatures detected.")


def visualize_data(df):
    """
    Create visualizations for temperature and humidity trends, and weather condition distributions.
    """
    # Line Plot for Temperature Trend
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x="date", y="temperature", marker="o", label="Temperature (°C)")
    plt.xticks(rotation=45)
    plt.title("Temperature Trend Over Time")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Line Plot for Humidity Trend
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x="date", y="humidity", marker="o", color="orange", label="Humidity (%)")
    plt.xticks(rotation=45)
    plt.title("Humidity Trend Over Time")
    plt.xlabel("Date")
    plt.ylabel("Humidity (%)")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Pie Chart for Weather Condition Frequency
    plt.figure(figsize=(8, 6))
    df['weather'].value_counts().plot.pie(autopct='%1.1f%%', startangle=140, shadow=True, cmap="tab10")
    plt.title("Weather Conditions Proportion")
    plt.ylabel("")
    plt.tight_layout()
    plt.show()


def weekly_average_trends(df):
    """
    Calculate and visualize weekly average trends for temperature and humidity.
    """
    df['week'] = df['date'].dt.isocalendar().week
    weekly_avg = df.groupby('week')[['temperature', 'humidity']].mean()

    fig, ax = plt.subplots(figsize=(10, 5))
    weekly_avg.plot(ax=ax, marker='o')

    ax.set_title("Weekly Average Temperature and Humidity")
    ax.set_xlabel("Week Number")
    ax.set_ylabel("Values")
    ax.grid()
    plt.tight_layout()
    plt.show()


def main():
    """
    Main function to control the workflow.
    """
    print("Welcome to the Weather Data Analysis Tool!")
    city = input("Enter the city name: ").strip()
    api_key = ''  # Replace with your actual API key

    fetch_weather_data(city, api_key)

    weather_data = pd.read_csv("weather_data.csv")
    weather_data['date'] = pd.to_datetime(weather_data['date'])

    while True:
        print("\n--- Options ---")
        print("1. Analyze Data")
        print("2. Visualize Data")
        print("3. Weekly Average Trends")
        print("4. Temperature Rolling Stats and Outliers")
        print("5. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            analyze_data(weather_data)
        elif choice == "2":
            visualize_data(weather_data)
        elif choice == "3":
            weekly_average_trends(weather_data)
        elif choice == "4":
            weather_data = calculate_rolling_stats(weather_data)
            plot_rolling_stats(weather_data)
        elif choice == "5":
            print("Thank you for using the Weather Data Analysis Tool!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
