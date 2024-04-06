from flask import Flask, render_template, request, redirect, url_for, abort, g, make_response, session, jsonify
import requests
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback
import os
import cv2
import face_recognition
import numpy as np
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from flask import Flask, Response


app = Flask(__name__)

# Define your API endpoints
FORKLIFTS_API = 'https://localhost:7128/Forklifts'
PALLETS_API = 'https://localhost:7128/Pallets'
SHELVES_API = 'https://localhost:7128/Shelves'
USERS_API = 'https://localhost:7128/Users'
TRACKING_LOG = 'https://localhost:7128/TrackingLogs'


# Global storage for the last received PubNub message
last_pubnub_message = {}

class MyListener(SubscribeCallback):
    def message(self, pubnub, message):
        global last_pubnub_message
        # Store the received message
        last_pubnub_message = message.message
        print(f"Received message: {last_pubnub_message}")

# PubNub configuration
pnconfig = PNConfiguration()
pnconfig.subscribe_key = 'sub-c-878f6650-7fba-4b01-bd5c-061c161b0e9a'
pnconfig.ssl = True
pnconfig.uuid = 'your_unique_identifier'

# Initialize and start listening on PubNub
pubnub = PubNub(pnconfig)
pubnub.add_listener(MyListener())
pubnub.subscribe().channels('face_recognition_channel').execute()

# Initialize PubNub
pnconfig = PNConfiguration()
pnconfig.publish_key = 'pub-c-9eb20452-d655-4bf0-91b9-8eecde9199e3'
pnconfig.subscribe_key = 'sub-c-878f6650-7fba-4b01-bd5c-061c161b0e9a'
pnconfig.ssl = True
pnconfig.uuid = 'unique_identifier_for_this_client'
pubnub = PubNub(pnconfig)


app.secret_key = 'AdminViewPySecretKey'

# Callback function for publish response
def publish_callback(result, status):
    if not status.is_error():
        print(f"Message published successfully: {result}")
    else:
        print(f"Failed to publish message: {status}")

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


# Load all images from the operatorimages folder and create encodings
image_folder = "operatorImages"
known_face_encodings = []
known_face_names = []
for filename in os.listdir(image_folder):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image_path = os.path.join(image_folder, filename)
        image = face_recognition.load_image_file(image_path)
        image_encodings = face_recognition.face_encodings(image)
        if image_encodings:
            face_encoding = image_encodings[0]
            person_name = os.path.splitext(os.path.basename(filename))[0]
            known_face_encodings.append(face_encoding)
            known_face_names.append(person_name)

def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            face_frame = frame[y:y + h, x:x + w]
            face_frame_rgb = cv2.cvtColor(face_frame, cv2.COLOR_BGR2RGB)
            current_face_encoding = face_recognition.face_encodings(face_frame_rgb)

            if current_face_encoding:
                matches = face_recognition.compare_faces(known_face_encodings, current_face_encoding[0])
                name = "Unknown"

                face_distances = face_recognition.face_distance(known_face_encodings, current_face_encoding[0])
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    print(f"Access Granted for {name}")

                    # Send message over PubNub
                    payload = {'userId': "string1", 'passCode': 'string', 'requestFromAdmin': True}
                    print(f"Sending message: {payload}")
                    pubnub.publish().channel('face_recognition_channel').message(payload).pn_async(publish_callback)
                else:
                    payload = {'userId': 'invalid', 'passCode': 'invalid', 'requestFromAdmin': True}
                    pubnub.publish().channel('face_recognition_channel').message(payload).pn_async(publish_callback)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global last_pubnub_message  # Access the global variable

    if request.method == 'POST':
        # Check if PubNub message contains required fields
        if 'userId' in last_pubnub_message and 'passCode' in last_pubnub_message:
            user_id = last_pubnub_message['userId']
            pass_code = last_pubnub_message['passCode']
            request_from_admin = last_pubnub_message.get('requestFromAdmin', False)
        else:
            # Handle the case where the required data is not available
            error_message = 'Required information is missing. Please try again.'
            return render_template('login.html', error=error_message)

        # Call the API to authenticate the user with the data from PubNub
        response = requests.post(f"{USERS_API}/Authenticate", params={
            'userId': user_id,
            'passCode': pass_code,
            'requestFromAdmin': request_from_admin
        }, verify=False)  # ensure verify is set appropriately for your environment

        if response.status_code == 200:
            # Successful login, store user_id in session
            session['user_id'] = user_id
            return redirect(url_for('index'))  # Redirect to the 'index' route or your intended destination
        else:
            # Login failed, show an error message
            error_message = 'Login failed, please try again.'
            return render_template('login.html', error=error_message)

    # For GET requests, render the login form
    return render_template('login.html')

@app.route('/get_last_message')
def get_last_message():
    global last_pubnub_message
    face_detected = last_pubnub_message.get('face_detected', False)
    return jsonify({'face_detected': face_detected})

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


@app.route('/createUser', methods=['GET', 'POST'])
def createUser():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_idOne = get_logged_in_user_id()
    user_data = get_user_data(user_idOne)
    if user_data:
        username = user_data.get('firstName')
    else:
        username = 'Guest'
    # Add user data to the API
# Fetch user data from the provided API
    response_users = requests.get(USERS_API, verify=False)
    if response_users.status_code == 200:
        users_data = response_users.json().get('users', [])
    else:
        users_data = []

    if request.method == 'POST':
        # Assuming the form data uses the same keys as your data structure
        new_data = {
            'id': request.form['id'],
            'userType': int(request.form['userType']),  # Convert to int as necessary
            'firstName': request.form['firstName'],
            'lastName': request.form['lastName'],
            'passcode': request.form['passcode'],
            'forkliftCertified': request.form['forkliftCertified'].lower() in ['true', '1', 't', 'y', 'yes'],  # Convert to boolean
            'incorrectPalletPlacements': int(request.form['incorrectPalletPlacements'])  # Convert to int as necessary
        }
        response = requests.post(USERS_API, json=new_data, verify=False)
        if response.status_code == 201:
            return redirect(url_for('index'))  # Ensure you have an 'index' route defined
    return render_template('createUser.html', users=users_data,username=username)


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
        pallet_entry = response.json()
    else:
        # Handle not found or other error scenarios
        # You can redirect to an error page or show an error message
        return 'Pallet data not found', 404

    if request.method == 'POST':
        # Process the form data and update the existing pallet data entry using the API
        updated_pallet_data = {
            'id': request.form['id'],  # You can choose to update the ID or not
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
        response = requests.put(f'{SHELVES_API}/{id}', json=updated_data, verify=False)
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
    app.run(debug=True)
