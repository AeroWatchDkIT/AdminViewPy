from flask import Flask, render_template, request, redirect, url_for, abort
import requests

app = Flask(__name__)

# Define your API endpoints
FORKLIFTS_API = 'https://localhost:7128/Forklifts'
PALLETS_API = 'https://localhost:7128/Pallets'
SHELVES_API = 'https://localhost:7128/Shelves'
USERS_API = 'https://localhost:7128/Users'

@app.route('/')
def index():
    # Fetch data from the Forklifts endpoint
    response_forklifts = requests.get(FORKLIFTS_API, verify=False)
    if response_forklifts.status_code == 200:
        forklifts_data = response_forklifts.json().get('entities', [])
    else:
        forklifts_data = []

    # Fetch user data from the provided API
    response_users = requests.get(USERS_API, verify=False)
    if response_users.status_code == 200:
        users_data = response_users.json().get('users', [])
    else:
        users_data = []

    # Check if both forklifts_data and users_data are empty, indicating a 404 error
    if not forklifts_data and not users_data:
        abort(404)

    return render_template('index.html', forklifts=forklifts_data, users=users_data)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.route('/user/<string:user_id>')
def view_user(user_id):
    # Fetch the user data by user_id from your API or database
    response = requests.get(f'{USERS_API}/{user_id}', verify=False)
    
    if response.status_code == 200:
        user = response.json()
    else:
        # Handle the case where the user is not found or an error occurs
        user = None

    return render_template('viewUsers.html', user=user)

# Create Forklift
@app.route('/createForklift', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # Process the form data and create a new data entry using the API
        new_data = {
            'id': request.form['id'],
            'lastUserId': request.form['lastUserId'],
            'lastUser': {
                'id': request.form['lastUserId'],
                'userType': int(request.form['userType']),  # Adjust as needed
                'firstName': request.form['firstName'],
                'lastName': request.form['lastName'],
                'passcode': request.form['passcode'],
                'forkliftCertified': True if request.form['forkliftCertified'] == 'true' else False,
                'incorrectPalletPlacements': int(request.form['incorrectPalletPlacements'])
            },
            'lastPalletId': request.form['lastPalletId'],
            'lastPallet': {
                'id': request.form['lastPalletId'],
                'state': int(request.form['state']),
                'location': request.form['location']
            }
        }
        # Send a POST request to your API to create the new data entry
        response = requests.post(FORKLIFTS_API, json={'entities': [new_data]}, verify=False)
        if response.status_code == 201:  # Assuming a successful creation status code
            # Redirect to the data listing page after successful creation
            return redirect(url_for('index'))
    
    # Display a form for creating new data
    return render_template('createForklift.html')

@app.route('/forklifts')
def forklifts():
    # Fetch data from the Forklifts endpoint
    response_forklifts = requests.get(FORKLIFTS_API, verify=False)
    if response_forklifts.status_code == 200:
        forklifts_data = response_forklifts.json().get('entities', [])
    else:
        forklifts_data = []
    # Fetch user data from the provided API
    response_users = requests.get(USERS_API, verify=False)
    if response_users.status_code == 200:
        users_data = response_users.json().get('users', [])
    else:
        users_data = []

    return render_template('forklifts.html', forklifts=forklifts_data, users=users_data)

@app.route('/forkliftsCharts')
def forkliftsCharts():
    # Fetch data from the Forklifts endpoint
    response_forklifts = requests.get(FORKLIFTS_API, verify=False)
    if response_forklifts.status_code == 200:
        forklifts_data = response_forklifts.json().get('entities', [])
    else:
        forklifts_data = []
    # Fetch user data from the provided API
    response_users = requests.get(USERS_API, verify=False)
    if response_users.status_code == 200:
        users_data = response_users.json().get('users', [])
    else:
        users_data = []

    return render_template('forkliftCharts.html', forklifts=forklifts_data, users=users_data)

# Update Forklift
@app.route('/editForklifts/<string:id>', methods=['GET', 'POST'])
def edit(id):
    # Fetch the existing data entry based on the provided ID
    response = requests.get(f'{FORKLIFTS_API}/{id}', verify=False)
    if response.status_code == 200:
        data_entry = response.json()
    else:
        # Handle not found or other error scenarios
        # You can redirect to an error page or show an error message
        return 'Data not found', 404
    
    if request.method == 'POST':
        # Process the form data and update the existing data entry using the API
        updated_data = {
            'id': request.form['id'],
            'lastUserId': request.form['lastUserId'],
            'lastUser': {
                'id': request.form['lastUserId'],
                'userType': 0,  # Adjust as needed
                'firstName': request.form['firstName'],
                'lastName': request.form['lastName'],
                'passcode': request.form['passcode'],
                'forkliftCertified': True if request.form['forkliftCertified'] == 'true' else False,
                'incorrectPalletPlacements': int(request.form['incorrectPalletPlacements'])
            },
            'lastPalletId': request.form['lastPalletId'],
            'lastPallet': {
                'id': request.form['lastPalletId'],
                'state': int(request.form['state']),
                'location': request.form['location']
            }
        }
        # Send a PUT request to your API to update the data entry
        response = requests.put(f'{FORKLIFTS_API}/{id}', json=updated_data, verify=False)
        if response.status_code == 200:  # Assuming a successful update status code
            # Redirect to the data listing page after successful update
            return redirect(url_for('index'))

    # Display a form for editing the existing data
    return render_template('editForklift.html', data=data_entry)

# Delete Forklift
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

@app.route('/pallets')
def pallets():
    # Fetch data from the Pallets endpoint
    pallet_response = requests.get(PALLETS_API, verify=False)
    if pallet_response.status_code == 200:
        pallets_data = pallet_response.json().get('pallets', [])
    else:
        pallets_data = []

    # Fetch user data from the provided API
    response_users = requests.get(USERS_API, verify=False)
    if response_users.status_code == 200:
        users_data = response_users.json().get('users', [])
    else:
        users_data = []

    return render_template('pallets.html', pallets=pallets_data, users=users_data)


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
        pallet_entry = response.json()
    else:
        # Handle not found or other error scenarios
        # You can redirect to an error page or show an error message
        return 'Pallet data not found', 404

    if request.method == 'POST':
        # Process the form data and update the existing pallet data entry using the API
        updated_pallet_data = {
            'id': id,
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

@app.route('/shelves')
def shelves():
    # Fetch data from the Shelves endpoint
    response_shelves = requests.get(SHELVES_API, verify=False)
    if response_shelves.status_code == 200:
        shelves_data = response_shelves.json().get('entities', [])
    else:
        shelves_data = []

    # Fetch user data from the provided API
    response_users = requests.get(USERS_API, verify=False)
    if response_users.status_code == 200:
        users_data = response_users.json().get('users', [])
    else:
        users_data = []

    return render_template('shelves.html', shelves=shelves_data, users=users_data)


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
        response = requests.post(SHELVES_API, json={'entities': [new_data]}, verify=False)
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