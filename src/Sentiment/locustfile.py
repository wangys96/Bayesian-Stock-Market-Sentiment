from locust import HttpLocust, TaskSet, task
import random
import json
with open("testcase","r") as f:
    latest=json.load(f)
class UserBehavior(TaskSet):
    @task(1)
    def home(self):
        self.client.get("/")

    @task(2)
    def search(self):
        self.client.get("/search")

    @task(3)
    def random_search(self):
        self.client.get("/search?target={}".format(latest[random.randint(0,len(latest)-1)]))

    @task(4)
    def hot(self):
        self.client.get("/hot")

    @task(5)
    def text(self):
        self.client.get("/text")


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 10000