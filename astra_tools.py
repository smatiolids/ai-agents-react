import os
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool
import os
from astra_conn import AstraDBConnection

astra_db = AstraDBConnection().get_session()
flight_tickets_collection = astra_db.get_collection(os.getenv("ASTRA_COLLECTION"))
CUSTOMER_ID = 'f08a6894-1863-491d-8116-3945fb915597'  # Mocked for testing

# TOOL Definition =  Scheduled Flights
class ScheduledFlightsInput(BaseModel):
    customer_id: str = Field(
        description="The UUID that represents the customer")
    conditions: dict = Field(
        description="The conditions for the fields: arrivalAirport, departureAirport, departureDateTime ")


@tool(args_schema=ScheduledFlightsInput)
def get_scheduled_flights(customer_id: str, conditions: dict) -> [str]:
    """Returns information about scheduled flights considering conditions for arrivalAirport, departureAirport, departureDateTime. Consider Airport codes and Dates in ISO format """
    filter = {"customerId": customer_id, **conditions}
    print(f"Scheduled flights condition: {conditions}")

    flights = flight_tickets_collection.find(filter=filter, projection={
                                              "departureAirport": 1, "arrivalAirport": 1, "departureDateTime": 1})
    
    res = []
    for doc in flights:
        res.append(doc)
    return doc


class ScheduledFlightDetailInput(BaseModel):
    ticket_id: str = Field(
        description="The UUID for a specific flight ticket")

# TOOL Definition =  Scheduled Flight  Detail
@tool(args_schema=ScheduledFlightDetailInput)
def get_flight_detail(ticket_id: str) -> [str]:
    """Returns information about on flight"""
    print(f"Flight detail: {ticket_id}")
    filter = {"_id": ticket_id}
    flight = flight_tickets_collection.find_one(filter=filter)
    return flight
