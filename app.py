from flask import Flask, render_template
import requests
from flask import request

app = Flask(__name__)

@app.route('/')
def index():
    # Fetch data from the Forklifts endpoint
    forklift_response = requests.get('https://localhost:7128/Forklifts', verify=False)
    if forklift_response.status_code == 200:
        forklifts_data = forklift_response.json().get('forklifts', [])  # Use .get for safer access
    else:
        forklifts_data = []

    # Fetch data from the Pallets endpoint
    pallet_response = requests.get('https://localhost:7128/Pallets', verify=False)
    if pallet_response.status_code == 200:
        pallets_data = pallet_response.json()  # Assuming this is a list directly
    else:
        pallets_data = []

    # Render data in a HTML template
    return render_template('index.html', forklifts=forklifts_data, pallets=pallets_data)

@app.route('/forklifts')
def forklifts():
    # Fetch data from the Forklifts endpoint
    search_term = request.args.get('search', '')  # 'search' is the query parameter name

    if search_term:
        # If a search term is provided, use the search endpoint
        response = requests.get(f'https://localhost:7128/Forklifts/search?SearchTerm={search_term}', verify=False)
    else:
        # If no search term is provided, fetch all forklift data
        response = requests.get('https://localhost:7128/Forklifts', verify=False)

    if response.status_code == 200: 
        forklifts_data = response.json().get('forklifts', []) # Assuming the search also wraps the data in a 'forklifts' key
    else:
        forklifts_data = []
    # Render data in a HTML template
    return render_template('forklifts.html', forklifts=forklifts_data)

if __name__ == '__main__':
    app.run(debug=True)
