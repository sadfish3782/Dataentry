from flask import Flask, render_template, request, jsonify
import csv
import os
from datetime import datetime
import re

app = Flask(__name__)

# Function to get the path for the current month's folder
def get_csv_file_path(process_name):
    current_year = datetime.now().strftime('%Y')
    current_month = datetime.now().strftime('%B')
    current_date = datetime.now().strftime('%d %b')

    base_folder = os.path.join(os.getcwd(), 'csv_data')
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)

    year_folder = os.path.join(base_folder, current_year)
    if not os.path.exists(year_folder):
        os.makedirs(year_folder)

    month_folder = os.path.join(year_folder, current_month)
    if not os.path.exists(month_folder):
        os.makedirs(month_folder)

    date_folder = os.path.join(month_folder, current_date)
    if not os.path.exists(date_folder):
        os.makedirs(date_folder)

    csv_file = os.path.join(date_folder, f"{process_name}.csv")
    return csv_file

# Function to clean the header names (removes parentheses content)
def clean_header(header_name):
    cleaned = re.sub(r'\(.*?\)', '', header_name).strip()
    print(f"Original header: {header_name} -> Cleaned header: {cleaned}")  # Debugging output
    return cleaned

@app.route('/')
def index():
    num_frames = 7  # Fixed number of frames for SPM
    return render_template('index.html', num_frames=num_frames)

@app.route('/second')
def second():
    num_frames = 8  # Fixed number of frames for SPM
    return render_template('second.html', num_frames=num_frames)

@app.route('/index')
def index_again(): #To go back to SPM Machine Window
    num_frames = 7  # Fixed number of frames for SPM
    return render_template('index.html', num_frames=num_frames)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Get the form data from the request
        data = request.form.to_dict()
        process_name = data.get(f"Process_Name")

        # Prepare to collect headers and values
        headers = []
        values = []

        # Add "Time" as the first header and its corresponding value
        current_time = datetime.now().strftime('%H:%M')  # Capture time in 24-hour format
        headers.append('Time')  # Add Time header
        values.append(current_time)  # Add the captured time value

        # Build headers and values dynamically
        for key, value in data.items():

            if key == 'Process_Name' or 'index' in key:
                    continue  # Skip Process_Name and index keys
            if 'index' in key:
                continue  # Skip index keys
            if 'Check' in key:  # Handle OK/NOK dropdowns
                values.append(True if value == 'true' else False)
            else:
                # Add to headers and values
                cleaned_header = clean_header(key)  # Clean header names
                headers.append(cleaned_header)  # Use cleaned header
                values.append(value if value else 'N/A')

        csv_file = get_csv_file_path(process_name)

        # Check if the CSV file exists; if not, create it with headers
        if not os.path.exists(csv_file):
            with open(csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)

                # Create header rows in pairs (spanning two cells if needed)
                header_row = []
                for i in range(len(headers)):
                    header_row.append(headers[i])
                    header_row.append('')  # Empty next cell for pair formatting

                writer.writerow(header_row)

        # Append values in pairs to the CSV file
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Create a value row corresponding to headers
            value_row = []
            for i in range(len(values)):
                value_row.append(values[i])
                value_row.append('')  # Empty next cell for pair formatting

            writer.writerow(value_row)

        # Return a success response in JSON format
        return jsonify({'status': 'success', 'data': data}), 200

    except Exception as e:
        print(f"Error processing form data: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
