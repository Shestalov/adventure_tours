# Adventure tours

Application allows you to crate a route (e.g. hiking, cycling).
Add event, review to route. Join to event or manage users if you are an admin. 
There is filtering of routes by type, country, location.
Login and registration are implemented and required for users.


**Install to docker and run mongo db:**

https://hub.docker.com/_/mongo

`$ docker run --name some-mongo -d mongo:tag`

**set up environment variable for connection to mongo**
* MONGO_HOST=127.0.0.1
* MONGO_PASSWORD=admin
* MONGO_PORT=27017
* MONGO_USERNAME=admin

**Install requirements**

`$ pip install -r requirements.txt`

**Run project**
