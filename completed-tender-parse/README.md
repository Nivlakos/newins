# All Tender Parsing microservice

Parse all tenders from [rostender](https://rostender.info) and save them to PostgreSQL database. Note that it's gonna take forever to import all of them with current approach, that's why it was moved out to a separate microservice to not disturb new/updated tenders parsing.

Configuration:

* Chrome profile to use for Selenium
* Username and password for signing in to *rostender* when no valid login token is found in cookies on the given Chrome profile
* Database connection details

