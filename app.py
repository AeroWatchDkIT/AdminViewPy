from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# Define your API endpoints
FORKLIFTS_API = 'https://localhost:7128/Forklifts'
PALLETS_API = 'https://localhost:7128/Pallets'
SHELVES_API = 'https://localhost:7128/Shelves'

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
@app.route('/createForklift', methods=['GET', 'POST'])
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
    return render_template('createForklift.html')

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
@app.route('/editForklifts/<string:id>', methods=['GET', 'POST'])
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
    return render_template('editForklift.html', data=data_entry)

# Delete Data (Delete)
@app.route('/deleteForklifts/<string:id>', methods=['GET', 'POST'])
def delete(id):
    if request.method == 'POST':
        # Send a DELETE request to your API to delete the data entry by ID
        response = requests.delete(f'{FORKLIFTS_API}/{id}', verify=False)
        if response.status_code == 204:  # Assuming a successful deletion status code
            # Redirect to the data listing page after successful deletion
            return redirect(url_for('index'))

    # Display a confirmation page for deleting the data
    return render_template('deleteForklift.html', id=id)

# Fetch Pallets Data (Read)
@app.route('/pallets')
def pallets():
    # Fetch data from the Pallets endpoint
    pallet_response = requests.get(PALLETS_API, verify=False)
    if pallet_response.status_code == 200:
        pallets_data = pallet_response.json()  # Assuming this is a list directly
    else:
        pallets_data = []

    return render_template('pallets.html', pallets=pallets_data)

# Create Pallet Data (Create)
@app.route('/createPallet', methods=['GET', 'POST'])
def create_pallet():
    if request.method == 'POST':
        # Process the form data and create a new pallet entry using the API
        new_pallet_data = {
            'id': request.form['id'],
            'state': int(request.form['state']),
            'location': request.form['location']
        }
        # Send a POST request to your Pallets API to create the new pallet entry
        response = requests.post(PALLETS_API, json=new_pallet_data, verify=False)
        if response.status_code == 201:  # Assuming a successful creation status code
            # Redirect to the pallets listing page after successful creation
            return redirect(url_for('pallets'))

    # Display a form for creating new pallet data
    return render_template('createPallet.html')

# Update Pallet Data (Update)
@app.route('/editPallet/<string:id>', methods=['GET', 'POST'])
def edit_pallet(id):
    # Fetch the existing pallet data entry based on the provided ID
    response = requests.get(f'{PALLETS_API}/{id}', verify=False)
    if response.status_code == 200:
        pallet_entry = response.json()  # Assuming your API provides data by ID
    else:
        # Handle not found or other error scenarios
        # You can redirect to an error page or show an error message
        return 'Pallet data not found', 404
    
    if request.method == 'POST':
        # Process the form data and update the existing pallet data entry using the API
        updated_pallet_data = {
            'state': int(request.form['state']),
            'location': request.form['location']
        }
        # Send a PUT request to your Pallets API to update the pallet data entry
        response = requests.put(f'{PALLETS_API}/{id}', json=updated_pallet_data, verify=False)
        if response.status_code == 200:  # Assuming a successful update status code
            # Redirect to the pallets listing page after successful update
            return redirect(url_for('pallets'))

    # Display a form for editing the existing pallet data
    return render_template('editPallet.html', pallet=pallet_entry)

# Delete Pallet Data (Delete)
@app.route('/deletePallet/<string:id>', methods=['GET', 'POST'])
def delete_pallet(id):
    if request.method == 'POST':
        # Send a DELETE request to your Pallets API to delete the pallet data entry by ID
        response = requests.delete(f'{PALLETS_API}/{id}', verify=False)
        if response.status_code == 204:  # Assuming a successful deletion status code
            # Redirect to the pallets listing page after successful deletion
            return redirect(url_for('pallets'))

    # Display a confirmation page for deleting the pallet data
    return render_template('deletePallet.html', id=id)

# List Shelves
@app.route('/shelves')
def shelves():
    response = requests.get(SHELVES_API, verify=False)
    if response.status_code == 200:
        shelves_data = response.json()
    else:
        shelves_data = []
    return render_template('shelves.html', shelves=shelves_data)

# Create Shelf
@app.route('/createShelf', methods=['GET', 'POST'])
def createShelf():
    if request.method == 'POST':
        new_data = {
            'id': request.form['id'],
            'palletId': request.form['palletId'],
            'pallet': None,  # Adjust this as needed
            'location': request.form['location']
        }
        response = requests.post(SHELVES_API, json=new_data, verify=False)
        if response.status_code == 201:
            return redirect(url_for('shelves'))
    
    return render_template('createShelf.html')

# Edit Shelf
@app.route('/editShelf/<string:id>', methods=['GET', 'POST'])
def editShelf(id):
    response = requests.get(f'{SHELVES_API}/{id}', verify=False)
    if response.status_code == 200:
        shelf_data = response.json()
    else:
        return 'Shelf not found', 404
    
    if request.method == 'POST':
        updated_data = {
            'palletId': request.form['palletId'],
            'location': request.form['location']
        }
        response = requests.put(f'{SHELVES_API}/{id}', json=updated_data, verify=False)
        if response.status_code == 200:
            return redirect(url_for('shelves'))
    
    return render_template('editShelf.html', shelf=shelf_data)

# Delete Shelf
@app.route('/deleteShelf/<string:id>', methods=['GET', 'POST'])
def deleteShelf(id):
    if request.method == 'POST':
        response = requests.delete(f'{SHELVES_API}/{id}', verify=False)
        if response.status_code == 204:
            return redirect(url_for('shelves'))
    
    return render_template('deleteShelf.html', id=id)


if __name__ == '__main__':
    app.run(debug=True)