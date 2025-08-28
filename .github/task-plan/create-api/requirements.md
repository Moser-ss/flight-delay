# Expose data through an API

In the prior exercise you created a model to predict the likelihood a flight will be delayed into an airport by more than 15 minutes on a given day of the week. Now it's time to expose both this model and the associated list of airports so you can create the front-end application.

## Defining success

You will have successfully completed the challenge after:

- creating an endpoint to accept the id of the day of week and airport, which calls the model and returns both the chances the flight will be delayed and the confidence percent of the prediction.
- creating an endpoint which returns the list of airport names and IDs, sorted in alphabetical order.
- all data is returned as JSON.


## Technical requirements
- Use FastAPI framework for API development https://fastapi.tiangolo.com/
- The source code of the API will be located in the server directory in repository root
- Use Python 3.11+
- The server will use the port 8080 