from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)  # Simulated users will wait 1-5 seconds between tasks

    @task
    def index_page(self):
        self.client.get("/")

    @task(2)  # This task is twice as likely to be executed
    def tracking_log(self):
        self.client.get("/trackingLog")

    @task(2)  # This task is twice as likely to be executed
    def forklifts(self):
        self.client.get("/forklifts")

    @task(2)  # This task is twice as likely to be executed
    def pallets(self):
        self.client.get("/pallets")

    @task(2)  # This task is twice as likely to be executed
    def shelves(self):
        self.client.get("/shelves")