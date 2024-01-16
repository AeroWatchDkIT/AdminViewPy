from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# Define your API endpoints
FORKLIFTS_API = 'https://localhost:7128/Forklifts'

@app.route('/')
def index():
    # Fetch data from the Forklifts endpoint
    response = requests.get(FORKLIFTS_API, verify=False)
    if response.status_code == 200:
        forklifts_data = response.json().get('forklifts', [])
    else:
        forklifts_data = []

    return render_template('index.html', forklifts=forklifts_data)

# Create Data (Create)
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # Process the form data and create a new data entry using the API
        new_data = {
            'id': request.form['id'],
            'lastUserId': request.form['lastUserId'],
            'lastUser': request.form['lastUser'],
            'lastPallet': request.form['lastPallet']
        }
        # Send a POST request to your API to create the new data entry
        response = requests.post(FORKLIFTS_API, json=new_data, verify=False)
        if response.status_code == 201:  # Assuming a successful creation status code
            # Redirect to the data listing page after successful creation
            return redirect(url_for('index'))
    
    # Display a form for creating new data
    return render_template('create.html')

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

# Update Data (Update)
@app.route('/edit/<string:id>', methods=['GET', 'POST'])
def edit(id):
    # Fetch the existing data entry based on the provided ID
    response = requests.get(f'{FORKLIFTS_API}/{id}', verify=False)
    if response.status_code == 200:
        data_entry = response.json()  # Assuming your API provides data by ID
    else:
        # Handle not found or other error scenarios
        # You can redirect to an error page or show an error message
        return 'Data not found', 404
    
    if request.method == 'POST':
        # Process the form data and update the existing data entry using the API
        updated_data = {
            'lastUserId': request.form['lastUserId'],
            'lastUser': request.form['lastUser'],
            'lastPallet': request.form['lastPallet']
        }
        # Send a PUT request to your API to update the data entry
        response = requests.put(f'{FORKLIFTS_API}/{id}', json=updated_data, verify=False)
        if response.status_code == 200:  # Assuming a successful update status code
            # Redirect to the data listing page after successful update
            return redirect(url_for('index'))

    # Display a form for editing the existing data
    return render_template('edit.html', data=data_entry)

# Delete Data (Delete)
@app.route('/delete/<string:id>', methods=['GET', 'POST'])
def delete(id):
    if request.method == 'POST':
        # Send a DELETE request to your API to delete the data entry by ID
        response = requests.delete(f'{FORKLIFTS_API}/{id}', verify=False)
        if response.status_code == 204:  # Assuming a successful deletion status code
            # Redirect to the data listing page after successful deletion
            return redirect(url_for('index'))

    # Display a confirmation page for deleting the data
    return render_template('delete.html', id=id)

if __name__ == '__main__':
    app.run(debug=True)