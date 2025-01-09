# Updated and New Tender Parsing microservice

Parse all new or updated tenders from [rostender](https://rostender.info) and save them to PostgreSQL database

Configuration:

* Chrome profile to use for Selenium
* Username and password for signing in to *rostender* when no valid login token is found in cookies on the given Chrome profile
* Database connection details

