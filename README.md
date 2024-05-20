# Project Name

## How to Run

### Flask Installation
```bash
# Install Flask
pip install flask

```
In order for the website to work properly, you must also run the backend code. If the backend code isn't working as expected, follow these steps:
- Open your package manager console in your ide for c#.
- Run the following command to drop the database (make sure this is the intended action):
```bash
drop-database
```
- After dropping the database, run the backend program again:

#### Once the database was dropped return to flask app and run app.py

## If the issue persists, try updating the database:
```bash
update-database

```

## Big note
- As api needed CORS whitelisting `api program.cs()` code had to include 
```bash 
app.UseCors(options =>
{
	options.WithOrigins("http://127.0.0.1:5000") // Adjust your allowed origins here
		.AllowAnyHeader()
		.AllowAnyMethod();
});
```


# Running Load Testing
```
pip install Locust 

py -m pip install Locust
```
### Load Testing 
```bash
py -m locust
```

### Dependancies

```bash
aiohttp==3.9.3
aiosignal==1.3.1
attrs==23.2.0
blinker==1.7.0
CacheControl==0.14.0
cachetools==5.3.3
cbor2==5.6.2
certifi==2024.2.2
cffi==1.16.0
charset-normalizer==3.3.2
click==8.1.7
colorama==0.4.6
cryptography==42.0.5
firebase==4.0.1
firebase-admin==6.5.0
Flask==3.0.3
frozenlist==1.4.1
gcloud==0.17.0
google-api-core==2.18.0
google-api-python-client==2.125.0
google-auth==2.29.0
google-auth-httplib2==0.2.0
google-cloud-core==2.4.1
google-cloud-firestore==2.16.0
google-cloud-storage==2.16.0
google-crc32c==1.5.0
google-resumable-media==2.7.0
googleapis-common-protos==1.63.0
grpcio==1.62.1
grpcio-status==1.62.1
httplib2==0.22.0
idna==3.6
itsdangerous==2.1.2
Jinja2==3.1.3
jws==0.1.3
MarkupSafe==2.1.5
msgpack==1.0.8
multidict==6.0.5
oauth2client==3.0.0
proto-plus==1.23.0
protobuf==4.25.3
pubnub==7.4.4
pyasn1==0.6.0
pyasn1_modules==0.4.0
pycparser==2.22
pycryptodome==3.4.3
pycryptodomex==3.20.0
PyJWT==2.8.0
pyparsing==3.1.2
Pyrebase==3.0.27
python-jwt==2.0.1
requests==2.31.0
requests-toolbelt==0.7.0
rsa==4.9
six==1.16.0
uritemplate==4.1.1
urllib3==2.2.1
Werkzeug==3.0.2
yarl==1.9.4
```
