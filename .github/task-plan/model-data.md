# Working with a dataset and machine learning

The scenario for this workshop revolves around a [dataset from the FAA](../data/flights.csv) which contains core information about flights in the US in 2013.
It contains the carrier, the date and time the flights took off and arrived (and their origin and destination), and information about delays including both
the time and a flag if it was more than 15 minutes. For this scenario you will explore and cleanse the data, build and export a model trained to show the percent chance
a flight will be delayed for a day of the week and an airport, and create a new CSV file containing the list of all airports and their associated IDs in the dataset.

> **NOTE:** The CSV file is in the [data](../data/) folder, and is named **flights.csv**.

## Defining success

You will have successfully completed this challenge after:

- cleansing the data by identifying null values and replacing them with an appropriate value (zero in this case).
- creating a model which provides the chances a flight will be delayed by more than 15 minutes for a given day and airport pair.
- saving the model to a file for use in an external application.
- creating a new file with the names and associated ids from the dataset of all airports.
