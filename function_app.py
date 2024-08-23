import azure.functions as func
import json
from azure.cosmosdb.table import TableService, Entity
import logging
import os

# testing the build process


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == 'POST':
        logging.info("Connecting to TableService...")

        connection_string = os.getenv("COSMOSDB_CONNECTION_STRING")
        service = TableService(endpoint_suffix="table.cosmos.azure.com", connection_string=connection_string)
        
        partition_key = 'site'
        row_key = 'visitor_count'
        table_name = 'site_visitors'

        logging.info(f"Fetching entity from table '{table_name}' with PartitionKey='{partition_key}' and RowKey='{row_key}'...")
        entry = service.get_entity(table_name, partition_key, row_key)
        logging.info(f"Entity fetched: {entry}")

        updated_visitors = entry['visitors'] + 1
        logging.info(f"Updated visitor count: {updated_visitors}")

        visitors_dict = {
            'PartitionKey': partition_key,
            'RowKey': row_key,
            'visitors': updated_visitors
        }

        logging.info("Inserting or replacing entity in table...")
        service.insert_or_replace_entity(table_name, visitors_dict)
        logging.info("Entity successfully inserted/replaced.")

        response_data = {
            "visitor_count": updated_visitors
        }

        logging.info("Returning JSON response...")
        return func.HttpResponse(
            json.dumps(response_data), 
            mimetype="application/json", 
            status_code=200
        )
    else:
        logging.warning("Invalid request method received.")
        return func.HttpResponse(
            json.dumps({"error": "Please send a POST Request"}), 
            mimetype="application/json", 
            status_code=405
        )
