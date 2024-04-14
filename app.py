from flask import Flask, render_template, request, redirect, url_for, abort, g, make_response, session, jsonify,Response
import requests


app = Flask(__name__)

# Define your API endpoints
FORKLIFTS_API = 'https://palletsyncapi.azurewebsites.net/Forklifts'
PALLETS_API = 'https://palletsyncapi.azurewebsites.net/Pallets'
SHELVES_API = 'https://palletsyncapi.azurewebsites.net/Shelves'
USERS_API = 'https://palletsyncapi.azurewebsites.net/Users'
TRACKING_LOG = 'https://palletsyncapi.azurewebsites.net/TrackingLogs'

app.secret_key = 'AdminViewPySecretKey'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['userId']
        pass_code = request.form['passCode']
        # Directly get a boolean value from the form input
        request_from_admin = request.form.get('requestFromAdmin', 'false').lower() == 'true'

        # Call the API to authenticate the user with the correct boolean type
        response = requests.post(f"{USERS_API}/Authenticate", params={
            'userId': user_id,
            'passCode': pass_code,
            'requestFromAdmin': request_from_admin
        },verify=False
        )  # ensure verify is set appropriately for your environment

        if response.status_code == 200:
            # Successful login, store user_id in session
            session['user_id'] = user_id
            return redirect(url_for('index'))
        else:
            # Login failed, you can flash a message or return to the login page with an error
            error_message = 'Login failed, please try again.'
            return render_template('login.html', error=error_message)

    # If it's a GET request, just render the login form
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Clear the user_id from the session
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Function to check if the user is logged in
def is_logged_in():
    return 'user_id' in session

# Function to get the logged-in user's ID
def get_logged_in_user_id():
    return session.get('user_id', None)

# Function to fetch user data from the API
def get_user_data(user_id):
    response = requests.get(f'{USERS_API}/{user_id}', verify=False)
    if response.status_code == 200:
        return response.json()
    return None


# Index route
@app.route('/')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))

    user_id = get_logged_in_user_id()
    user_data = get_user_data(user_id)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'

    # Fetch data from the Forklifts endpoint
    response_forklifts = requests.get(FORKLIFTS_API, verify=False)
    forklifts_data = response_forklifts.json().get('entities', []) if response_forklifts.status_code == 200 else []

    # Fetch user data from the provided API
    response_users = requests.get(USERS_API, verify=False)
    users_data = response_users.json().get('users', []) if response_users.status_code == 200 else []

    if not forklifts_data and not users_data:
        # Directly render the 404 template with user data and set the status code to 404
        response = make_response(render_template('404.html', users=users_data), 404)
        return response

    # Render the index page with forklift and user data if both datasets are present
    return render_template('index.html', forklifts=forklifts_data, users=users_data, username=username)


# Tracking log route
@app.route('/trackingLog')
def trackingLog():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_id = get_logged_in_user_id()
    user_data = get_user_data(user_id)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'

    response_trackingLog = requests.get(TRACKING_LOG, verify=False)
    trackingLog_data = response_trackingLog.json().get('entities', []) if response_trackingLog.status_code == 200 else []

    response_users = requests.get(USERS_API, verify=False)
    users_data = response_users.json().get('users', []) if response_users.status_code == 200 else []

    return render_template('trackingLog.html', trackingLog=trackingLog_data, users=users_data,username=username)


@app.errorhandler(404)
def not_found(error):
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_idOne = get_logged_in_user_id()
    user_data = get_user_data(user_idOne)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'

    # Fetch user data from the same API as in the index route
    response_users = requests.get(USERS_API, verify=False)
    if response_users.status_code == 200:
        users_data = response_users.json().get('users', [])
    else:
        users_data = []

    # Render the custom 404 page with user data
    return render_template('404.html', users=users_data,username=username), 404



@app.route('/user/<string:user_id>')
def view_user(user_id):
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_idOne = get_logged_in_user_id()
    user_data = get_user_data(user_idOne)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'
    # Fetch the user data by user_id from your API or database
    response = requests.get(f'{USERS_API}/{user_id}', verify=False)
    response_users = requests.get(USERS_API, verify=False)
    
    if response_users.status_code == 200:
        userData = response_users.json().get('users', [])
    else:
        # Handle the case where the user is not found or an error occurs
        userData = None 

    if response.status_code == 200:
        user = response.json()
    else:
        # Handle the case where the user is not found or an error occurs
        user = None
    return render_template('viewUsers.html', user=user,userLoop=userData,username=username)

@app.route('/deleteUser/<string:id>', methods=['GET', 'POST'])
def deleteUser(id):
    # Directly redirect GET requests to the index to avoid showing the deletion URL.
    if request.method == 'GET':
        return redirect(url_for('index'))
    
    # Handle POST request: Attempt to delete the user.
    if request.method == 'POST':
        response = requests.delete(f'{USERS_API}/{id}', verify=False)
        if response.status_code == 204:  # Assuming 204 means success
            return redirect(url_for('index'))
    
    # If neither condition is met, it's a fallback, though this should not happen with the above logic.
    return redirect(url_for('index'))


@app.route('/createUser', methods=['POST'])
def createUser():
    if not is_logged_in():
        return redirect(url_for('login'))

    # Check if the request has a JSON body
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 400

    # Get data from the JSON request body
    data = request.get_json()

    # You can now use the data as you need, for example:
    new_user_data = {
        'id': data.get('id'),
        'userType': data.get('UserType'),
        'firstName': data.get('FirstName'),
        'lastName': data.get('LastName'),
        'passcode': data.get('Passcode'),
        'forkliftCertified': data.get('ForkliftCertified'),
        'incorrectPalletPlacements': data.get('IncorrectPalletPlacements'),
        'correctPalletPlacements': data.get('CorrectPalletPlacements'), # Assuming you want this field too
        'imageFilePath': data.get('ImageFilePath')  # If you are handling file paths
        # If you are handling file uploads, you need to use request.files['image'] or similar
    }

    # Handle image file if included
    if 'image' in request.files:
        # You will need to save the file and handle it as required by your application
        image_file = request.files['image']
        image_file.save('path_to_save_image')

    # Perform your API call to create the new user
    response = requests.post(USERS_API, json=new_user_data, verify=False)  # Note: verify should usually be True for SSL

    if response.status_code == 201:
        # If creation is successful
        return jsonify({"message": "User created successfully"}), 201
    else:
        # If there is an error from the API
        return jsonify(response.json()), response.status_code

    # Return a successful JSON response if no POST or if POST is handled correctly
    return jsonify({"message": "User creation page"}), 200


# Create Forklift
@app.route('/createForklift', methods=['GET', 'POST'])
def create():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_idOne = get_logged_in_user_id()
    user_data = get_user_data(user_idOne)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'

    if request.method == 'POST':
        # Process the form data and create a new data entry using the API
        new_data = {
            'id': request.form['id'],
        }
        # Send a POST request to your API to create the new data entry
        response = requests.post(FORKLIFTS_API, json=new_data, verify=False)
        if response.status_code == 201:  # Assuming a successful creation status code
            # Redirect to the data listing page after successful creation
            return redirect(url_for('index'))
    
    # Display a form for creating new data
    return render_template('createForklift.html', username=username)

@app.route('/forklifts')
def forklifts():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_idOne = get_logged_in_user_id()
    user_data = get_user_data(user_idOne)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'
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

    return render_template('forklifts.html', forklifts=forklifts_data, users=users_data,username=username)

@app.route('/forkliftsCharts')
def forkliftsCharts():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_idOne = get_logged_in_user_id()
    user_data = get_user_data(user_idOne)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'
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

    return render_template('forkliftCharts.html', forklifts=forklifts_data, users=users_data,username=username)

# Update Forklift
@app.route('/editForklifts/<string:id>', methods=['GET', 'POST'])
def edit(id):
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_idOne = get_logged_in_user_id()
    user_data = get_user_data(user_idOne)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'
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
        }
        # Send a PUT request to your API to update the data entry
        response = requests.put(f'{FORKLIFTS_API}/{id}', json=updated_data, verify=False)
        if response.status_code == 200:  # Assuming a successful update status code
            # Redirect to the data listing page after successful update
            return redirect(url_for('index'))

    # Display a form for editing the existing data
    return render_template('editForklift.html', data=data_entry,username=username)

# Delete Forklift
@app.route('/deleteForklifts/<string:id>', methods=['GET', 'POST'])
def delete(id):
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_idOne = get_logged_in_user_id()
    user_data = get_user_data(user_idOne)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'
    if request.method == 'POST':
        # Send a DELETE request to your API to delete the data entry by ID
        response = requests.delete(f'{FORKLIFTS_API}/{id}', verify=False)
        if response.status_code == 204:  # Assuming a successful deletion status code
            # Redirect to the data listing page after successful deletion
            return redirect(url_for('forklifts'))

    # Display a confirmation page for deleting the data
    return render_template('deleteForklift.html', id=id,username=username)

@app.route('/pallets')
def pallets():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_idOne = get_logged_in_user_id()
    user_data = get_user_data(user_idOne)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'
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

    return render_template('pallets.html', pallets=pallets_data, users=users_data,username=username)

@app.route('/palletCharts')
def palletCharts():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_idOne = get_logged_in_user_id()
    user_data = get_user_data(user_idOne)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'
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

    return render_template('palletCharts.html', pallets=pallets_data, users=users_data,username=username)

# Create Pallet Data (Create)
@app.route('/createPallet', methods=['GET', 'POST'])
def create_pallet():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_idOne = get_logged_in_user_id()
    user_data = get_user_data(user_idOne)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'

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
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_idOne = get_logged_in_user_id()
    user_data = get_user_data(user_idOne)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'

    # Fetch the existing pallet data entry based on the provided ID
    response = requests.get(f'{PALLETS_API}/{id}', verify=False)
    if response.status_code == 200:
        pallet_data = response.json()
    else:
        return 'Pallet data not found', 404

    if request.method == 'POST':
        updated_pallet_data = {
            'id': request.form['id'],  # You can choose to update the ID or not
            'state': int(request.form['state']),
            'location': request.form['location']
        }
        # Send a PUT request to your Pallets API to update the pallet data entry
        response = requests.put(f'{PALLETS_API}', json=updated_pallet_data, verify=False)
        if response.status_code == 200:  # Assuming a successful update status code
            return redirect(url_for('pallets'))

    # Display a form for editing the existing pallet data
    return render_template('editPallet.html', pallet=pallet_data,username=username)

 


# Delete Pallet Data (Delete)
@app.route('/deletePallet/<string:id>', methods=['GET', 'POST'])
def delete_pallet(id):
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_idOne = get_logged_in_user_id()
    user_data = get_user_data(user_idOne)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'
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
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_idOne = get_logged_in_user_id()
    user_data = get_user_data(user_idOne)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'
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

    return render_template('shelves.html', shelves=shelves_data, users=users_data,username=username)


# Create Shelf
@app.route('/createShelf', methods=['GET', 'POST'])
def createShelf():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_idOne = get_logged_in_user_id()
    user_data = get_user_data(user_idOne)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'
    if request.method == 'POST':
        new_data = {
            'id': request.form['id'],
            'palletId': request.form['palletId'],
            # 'pallet': None,  # Adjust this as needed
            'location': request.form['location']
        }
        response = requests.post(SHELVES_API, json={'entities': [new_data]}, verify=False)
        if response.status_code == 201:
            return redirect(url_for('shelves'))
    
    return render_template('createShelf.html')

# Edit Shelf
@app.route('/editShelf/<string:id>', methods=['GET', 'POST'])
def editShelf(id):
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_idOne = get_logged_in_user_id()
    user_data = get_user_data(user_idOne)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'
    response = requests.get(f'{SHELVES_API}/{id}', verify=False)
    if response.status_code == 200:
        shelf_data = response.json()
    else:
        return 'Shelf not found', 404
    
    if request.method == 'POST':
        updated_data = {
            'id': request.form['id'],
            'palletId': request.form['palletId'],
            'location': request.form['location']
        }
        response = requests.put(f'{SHELVES_API}', json=updated_data, verify=False)
        if response.status_code == 200:
            return redirect(url_for('shelves'))
    
    return render_template('editShelf.html', shelf=shelf_data,username=username)

# Delete Shelf
@app.route('/deleteShelf/<string:id>', methods=['GET', 'POST'])
def deleteShelf(id):
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_idOne = get_logged_in_user_id()
    user_data = get_user_data(user_idOne)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'
    if request.method == 'POST':
        response = requests.delete(f'{SHELVES_API}/{id}', verify=False)
        if response.status_code == 204:
            return redirect(url_for('shelves'))
    
    return render_template('index.html', id=id,username=username)

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000)
    app.run(debug=True, threaded=True)
