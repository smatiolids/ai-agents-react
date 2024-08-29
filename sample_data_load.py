import json
import os
from astra_conn import AstraDBConnection


### Prompt for generating the json file using OpenAI

# generate a sample json file with flight tickets considering the following attributes:
# _id 
# passengerId
# passengerName
# flightNumber
# departureAirport
# arrivalAirport
# departureDateTime
# arrivalDateTime
# seatNumber
# ticketClass
# ticketPrice
# bookingDate
# bookingReference

file_path = "./sample_data.json"

def load_flight_tickets(clear):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r') as file:
        data = json.load(file)

    if data['flights']:
        astra_db = AstraDBConnection().get_session()
        print("Creating or Getting the collection")
        flight_tickets_collection = astra_db.create_collection(os.getenv("ASTRA_COLLECTION"))
        
        print("Inserting Data")
        # flight_tickets_collection = astra_db.get_collection(os.getenv("ASTRA_COLLECTION"))
        res = flight_tickets_collection.insert_many([{**d, "customerId": os.getenv("CUSTOMER_ID")} for d in data['flights']])
        return res

    
    return False