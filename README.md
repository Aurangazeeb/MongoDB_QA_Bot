# Question Answering System Using LLM and MongoDB

This document details about how to get started with using this command
line app.

## Configuring the MongoDB Database
1. Install MongoDB community edition by referring to [their documentation](https://www.mongodb.com/docs/manual/administration/install-community/)
2. This project makes use of MongoDB version 8.0.0
3. Once installed make sure that MongoDB server is running using the command `sudo systemctl status mongod` and if not running use the
command `sudo systemctl start mongod`
4. Obtain the connection string using the command `grep -E 'bindIp|port' /etc/mongod.conf
`. By default, it is `mongodb://localhost:27017`.
5. Rename the `.env.sample` file to `.env`, which contains default as well as placeholder
values associated with all the secrets in the projects.
6. If the mongodb connection string is different in your case please replace the
`MONGODB_CONNECTION_STRING` variable value with yours.
7. You have the option to specify the database name as well as the collection name -
the default values are set to be `qa_system` and `stats` respectively.
8. The sample data to populate the database is specified as `DOC_PATH` in the `.env`
file and by default it is set to `./data/sample_documents.json`, which has
15 documents in the format mentioned in the requirement.
9. Once all the variables associated with MongoDB is set, then proceed to run
the bash script `setup_db.sh` by ensuring that it is converted into an executable
first using the command `chmod +x setup_db.sh`. This script will create the sample
`stats` collection as per requirement.

## Running the Command-Line App
1. After the database is setup, make sure to install all dependencies using `pip install -r requirements.txt`
2. The LLM backend used in this project is OpenAI, hence make sure to update the
`OPENAI_API_KEY` variable value in `.env` file before proceeding.
3. Then the app can be used via the command below:
`python app.py -q <your query>`

## Example usage
Run the command : 

`python app.py -q "How much of North America's economy is contributed by services in 2023?"`

Output : 
`"The economy of North America in 2023 is contributed by services at a rate of 65%."`

## Bonus Features Implemented

1. Caching - an in-memory cache is implemented that has a life span equal
to that of the `QueryHandler` class in `handle_query.py`
2. Supports aggregation queries - the bot can classify user queries
into aggregation or non-aggregation type and then create the corresponding mongodb
queries and eventually the natural response version of it.

## Testing App Functionalities
The app functionality testing is automated via `run_system_test.sh` bash script.
Make sure to convert it to an executable before running it.

**Note** : Inspite of many iterations of prompt engineering and inclusion of
techniques like few-shot learning, due to the stochastic behaviour of LLM on
rare occassions one or two of the tests may fail. In such a case, please run the bash script again