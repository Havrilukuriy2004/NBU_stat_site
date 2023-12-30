from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
from datetime import datetime

import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('Agg')
app = Flask(__name__)

def read_options_from_file(filename):
    options = {}
    with open(filename, 'r') as file:
        for line in file:
            key, name = line.strip().split(' - ')
            options[key] = name
    return options

@app.route('/')
def index():
    options = read_options_from_file('options.txt')
    add_options_1 = read_options_from_file('add_options_1.txt')
    time_options =  read_options_from_file('time_freq.txt')
    type_activity = read_options_from_file('types_activity.txt')
    type_of_gdp = read_options_from_file('type_of_gdp.txt')
    return render_template('index.html', options=options, add_options_1=add_options_1, time_options=time_options, type_activity=type_activity, type_of_gdp=type_of_gdp)

def get_exchange_rate(valcode, start_date, end_date):
    """
    Fetch exchange rates from the National Bank of Ukraine's API, save them to an Excel file, and plot the exchange rate graph.
    """
    # Convert date format
    start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y%m%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y%m%d')

    # Construct the URL
    url = f"https://bank.gov.ua/NBU_Exchange/exchange_site?start={start_date}&end={end_date}&valcode={valcode}&sort=exchangedate&order=desc&json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Load data into a DataFrame
        df = pd.DataFrame(data)
        if not df.empty:
            df = df[['exchangedate', 'rate']]
            df['exchangedate'] = pd.to_datetime(df['exchangedate'], format='%d.%m.%Y')

            # Save to Excel
            excel_filename = 'static/download.xlsx'
            df.to_excel(excel_filename, index=False)

            # Plot the exchange rate graph
            plt.figure(figsize=(10, 6))
            plt.plot(df['exchangedate'], df['rate'], marker='o')
            plt.title(f'Exchange Rate Dynamics: {valcode}')
            plt.xlabel('Date')
            plt.ylabel('Exchange Rate')
            plt.grid(True)
            plt.xticks(rotation=45)

            # Save the plot as an image
            plot_filename = 'static/exchange_rate_plot.png'
            plt.savefig(plot_filename)

            return plot_filename, excel_filename

    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

    return None, None


# Usage
# Replace these values with the actual inputs
# get_exchange_rate('USD', '2023-01-01', '2023-01-31')


@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    selected_option = data.get('selectedOption')
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    additional_option = data.get('additionalOption', None)
    option_three_value1 = data.get('optionThreeValue1', None)
    option_three_value2 = data.get('optionThreeValue2', None)
    option_three_value3 = data.get('optionThreeValue3', None)

    print(start_date)

    if selected_option == "op2":
        get_exchange_rate(additional_option, start_date, end_date)

    if selected_option == "op2":
        plot_filename, excel_filename = get_exchange_rate(additional_option, start_date, end_date)
        if plot_filename and excel_filename:
            return jsonify({'success': True, 'plotUrl': plot_filename, 'excelUrl': excel_filename})
        else:
            return jsonify({'success': False, 'error': 'Failed to fetch or process data'})

    # Повернення відповіді клієнту
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)
