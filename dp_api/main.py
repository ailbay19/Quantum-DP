import matplotlib.pyplot as plt
import numpy as np
import statistics
import pandas as pd
import math
import random
import csv
import sys
from quantum_api import get_quantum_numbers

from scipy.stats import wasserstein_distance

def read_dataset(file_path):
    dataset = pd.read_csv(file_path)
    return dataset.dropna()

def get_histogram(dataset, country='Turkey', year='2010'):
    filtered_data = dataset.query("Country == @country and dt.str.contains(@year)")
    avg_temperatures = filtered_data["AverageTemperature"].to_list()
    # plt.bar(filtered_data["dt"], avg_temperatures)
    # plt.xticks(rotation=60)
    # plt.title('Average Temperature Case for Country ' + country + ' in year ' + year)
    # plt.show()

    return avg_temperatures
def python_random_laplace(loc, scale, size=1):
    samples = []

    for _ in range(size):
        U = np.random.uniform()

        if U >= 0.5:
            sample = loc - scale * np.log(2.0 - 2.0 * U)
        else:
            sample = loc + scale * np.log(2.0 * U)

        samples.append(sample)

    return np.array(samples)

def quantum_random_laplace(loc, scale, size=1):
    # return python_random_laplace(loc, scale, size)
    samples = []
    api_key = 'NULL'

    if 1 <= size <= 1024:
        json = get_quantum_numbers(api_key, length=size, data_type='uint8')
        quantum_data = json['data']
    else:
        print("Random number size should be between 1 and 1024")
        sys.exit()

    samples = []
    # Scale the quantum data to the range [0, 1]
    scaled_data = [x / 255.0 for x in quantum_data]

    for U in scaled_data:
        if U >= 0.5:
            sample = loc - scale * np.log(2.0 - 2.0 * U)
        else:
            sample = loc + scale * np.log(2.0 * U)
        samples.append(sample)

        return np.array(samples)

def get_pseudorandom_dp_histogram(dataset, country, year, epsilon, N):
    filtered_data = dataset.query(f"Country == '{country}' and dt.str.contains('{year}')")
    avg_temperatures = filtered_data["AverageTemperature"].values
    sensitivity = N
    laplace_noise = python_random_laplace(loc=0, scale=sensitivity / epsilon, size=len(avg_temperatures))
    noisy_data = avg_temperatures + laplace_noise
    # plt.bar(filtered_data["dt"], noisy_data)
    # plt.xticks(rotation=60)
    # plt.title('Average Temperature Case for Country ' + country + ' in year ' + year)
    # plt.show()

    return noisy_data

def get_true_random_dp_histogram(dataset, country, year, epsilon, N):
    filtered_data = dataset.query(f"Country == '{country}' and dt.str.contains('{year}')")
    avg_temperatures = filtered_data["AverageTemperature"].values
    sensitivity = N
    quantum_laplace_noise =quantum_random_laplace(loc=0,scale=sensitivity / epsilon, size=len(avg_temperatures))
    noisy_data = avg_temperatures + quantum_laplace_noise
    # plt.bar(filtered_data["dt"], noisy_data)
    # plt.xticks(rotation=60)
    # plt.title('Average Temperature Case for Country ' + country + ' in year ' + year)
    # plt.show()

    return noisy_data

def country_year_query(country, year, epsilon_budget = 1):
    filename = "GlobalLandTemperaturesByCountry.csv"
    dataset = read_dataset(filename)

    country = country.title() # Capitalizes first letter

    # Transform numpy arrays to lists. 
    avg_temperatures_real = get_histogram(dataset,country,year)
    avg_temperatures_dp = get_pseudorandom_dp_histogram(dataset, country, year,epsilon_budget,1).tolist()
    avg_temperatures_quantum_dp = get_true_random_dp_histogram(dataset, country, year,epsilon_budget,1).tolist()

    return [avg_temperatures_real, avg_temperatures_dp, avg_temperatures_quantum_dp]

def get_noised(query, epsilon, sensitivity):
    laplace_noise = python_random_laplace(loc=0, scale=sensitivity / epsilon, size=len(query))
    quantum_laplace_noise = quantum_random_laplace(loc=0,scale=sensitivity / epsilon, size=len(query))
    print(f"\nNOISING LOG: \n\tSCALE:{sensitivity/epsilon}\n\tMAX:{max(laplace_noise)}, {max(quantum_laplace_noise)}")
    pseudo = query + laplace_noise
    true = query + quantum_laplace_noise
    
    return [pseudo, true]

# Returns 4x3 array of max, median, mean, min
#   with rows: original, pseudo, true
def country_all_queries(country, epsilon_budget = 10):
    filename = "GlobalLandTemperaturesByCountry.csv"
    dataset = read_dataset(filename)

    country = country.title() # Capitalizes first letter

    dataset['year'] = dataset['dt'].str[:4]

    df = dataset.loc[dataset["Country"] == country]

    query_max = df.groupby(['year'])['AverageTemperature'].max().dropna()
    query_median = df.groupby(['year'])['AverageTemperature'].median().dropna()
    query_mean = df.groupby(['year'])['AverageTemperature'].mean().dropna()
    query_min = df.groupby(['year'])['AverageTemperature'].min().dropna()

    noised_max = get_noised(query_max, epsilon_budget, 76)
    noised_median = get_noised(query_median, epsilon_budget, 76)
    noised_mean = get_noised(query_mean, epsilon_budget, 76/len(query_mean))
    noised_min = get_noised(query_min, epsilon_budget, 76)

    return [[query_max, *noised_max], [query_median, *noised_median],[query_mean, *noised_mean],[query_min, *noised_min]]


## Returns Earth Mover Distances between pairs of original, pseudo and real.
def get_errors_between(original, pseudo, real):
    e1 = wasserstein_distance(original, pseudo)
    e2 = wasserstein_distance(original, real)
    e3 = wasserstein_distance(real, pseudo)

    return [e1, e2, e3]

def main():
    filename = "GlobalLandTemperaturesByCountry.csv"
    dataset = read_dataset(filename)

    country = "Somalia"
    year = "2010"

    avg_temperatures_real = get_histogram(dataset,country,year)
    print(avg_temperatures_real)
    avg_temperatures_dp = get_pseudorandom_dp_histogram(dataset, country, year,10,1)
    print(avg_temperatures_dp)
    avg_temperatures_quantum_dp = get_true_random_dp_histogram(dataset, country, year,10,1)
    print(avg_temperatures_quantum_dp)

    return [avg_temperatures_real, avg_temperatures_dp, avg_temperatures_quantum_dp]

# Press the green button in the gutter to run the script.
if __name__ == "__main__":
        main()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
