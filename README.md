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
### Load Testing 
```bash
py -m locust
```