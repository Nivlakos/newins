# Tenders database (Postgre)

The app uses a Postgre database to save parsed tenders. [An official Docker image](https://hub.docker.com/_/postgres) can be used or a self-installed Postgre instance. Connection string must be provided in each other microservice configuration.

Please note there is no backup here. That's because database migrations (flask-migrate) will create each missing database object where required. The database backup only makes sense for this app if you want to copy all parsed data from one server to another in which case please make sure the migrations database table is also copied as is.


