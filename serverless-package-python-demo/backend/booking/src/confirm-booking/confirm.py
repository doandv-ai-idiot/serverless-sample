import os
import secrets
import boto3
from botocore.exceptions import ClientError

session = boto3.Session()
dynamodb = session.resource('dynamodb')
table_name = os.getenv("BOOKING_TABLE_NAME", 'bookings')

table = dynamodb.Table(table_name)


class BookingConfirmationException(Exception):
    def __init__(self, message=None, details=None):
        self.message = message or "Booking confirmation failed"
        self.details = details or {}


def confirm_booking(booking_id):
    reference = secrets.token_urlsafe(4)
    print("Booking Confirmation :{} , {}".format(booking_id, reference))
    try:
        ret = table.update_item(
            Key={"id": booking_id},
            ConditionExpression="id = :idVal",
            UpdateExpression="SET bookingReference = :br, #STATUS = :confirmed",
            ExpressionAttributeNames={"#STATUS": "status"},
            ExpressionAttributeValues={
                ":br": reference,
                ":idVal": booking_id,
                ":confirmed": "CONFIRMED"
            },
            ReturnValues="UPDATE_NEW"
        )
        return {"bookingReference": reference}
    except ClientError as err:
        raise BookingConfirmationException(details=err)


def lambda_handler(event, context):
    booking_id = event.get("bookingId")
    if not booking_id:
        raise ValueError("Invalid booking ID")
    try:
        ret = confirm_booking(booking_id)
        return ret["bookingReference"]
    except BookingConfirmationException as err:
        raise
