import base64
import json
import logging
import functions_framework
import re

from datetime import datetime
from google.cloud import storage, vision, bigquery

#Triggered from a message on a Cloud Pub/Sub topic
@functions_framework.cloud_event
def demo(cloud_event):
    #Retrieve the Pub/Sub message from the CloudEvent
    #cloud_event.data is a dict; 'message' holds the Pub/Sub message
    message = cloud_event.data.get("message")
    if not message:
        print("No Pub/Sub message found in the event data.")
        return

    #Decode the Base64-encoded message payload
    data = message.get("data")
    if not data:
        print("No 'data' field in the Pub/Sub message.")
        return

    try:
        payload_str = base64.b64decode(data).decode("utf-8")
        attributes = json.loads(payload_str)
    except Exception as e:
        print(f"Error decoding or parsing Pub/Sub message: {e}")
        return

    #Extract bucket and file name from the payload
    bucket_name = attributes.get("bucketId")
    file_name = attributes.get("objectId")

    if not bucket_name or not file_name:
        print("Missing 'bucketId' or 'objectId' in the message payload.")
        return

    #Perform OCR with Cloud Vision
    #Initialize Cloud clients
    storage_client = storage.Client()
    vision_client = vision.ImageAnnotatorClient()
    bq_client = bigquery.Client()

    #Construct GCS URI and run Vision OCR
    image_uri = f"gs://{bucket_name}/{file_name}"
    image = vision.Image()
    image.source.image_uri = image_uri

    response = vision_client.text_detection(image=image)
    texts = response.text_annotations

    #Extract text or return empty if none found
    extracted_text = texts[0].description if texts else ""
    print(f"Extracted text: {extracted_text}")
    logging.info(f"Extracted text: {extracted_text}")

    #Match against the updated car plate pattern
    car_plate_pattern = re.compile(r"\b[A-Z]{1,3} [0-9]{1,4}\b")
    matches = car_plate_pattern.findall(extracted_text)
    if matches:
        #Assume the desired plate is the first match
        car_plate = matches[0]
        print(f"Matched car plate: {car_plate}")
        logging.info(f"Matched car plate: {car_plate}")

    else:
        print(f"No match for {extracted_text}")

    #Insert result into BigQuery
    bq_client = bigquery.Client()
    table_ref = bq_client.dataset("car_plate_dataset").table("car_toll")
    
    #Define current datetime and out_toll_id
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    out_toll_id = 2

    #Query the car_toll table to check for the car plate
    query = f"""
        SELECT id, car_plate, out_datetime
        FROM `car_plate_dataset.car_toll`
        WHERE car_plate = '{car_plate}'
    """
    results = bq_client.query(query)
    car_toll_row = [row for row in results]

    if car_toll_row:
        #Car plate exists, update the out_datetime and out_toll_id
        update_query = f"""
            UPDATE `car_plate_dataset.car_toll`
            SET out_datetime = '{current_datetime}', out_toll_id = {out_toll_id}
            WHERE car_plate = '{car_plate}'
        """
        bq_client.query(update_query)

        #Update the balance in the car_owner table
        owner_query = f"""
            SELECT id, balance
            FROM `car_plate_dataset.car_owner`
            WHERE car_plate_number = '{car_plate}'
        """
        owner_results = bq_client.query(owner_query)
        owner_row = [row for row in owner_results]

        if owner_row:
            owner_id = owner_row[0].id
            current_balance = owner_row[0].balance
            new_balance = current_balance - 1.50

            balance_update_query = f"""
                UPDATE `car_plate_dataset.car_owner`
                SET balance = {new_balance}
                WHERE id = {owner_id}
            """
            bq_client.query(balance_update_query)

            print(f"Updated balance for car plate {car_plate}: New balance = {new_balance}")
            logging.info(f"Updated balance for car plate {car_plate}: New balance = {new_balance}")
        else:
            print(f"Car plate {car_plate} not found in car_owner table.")
            logging.info(f"Car plate {car_plate} not found in car_owner table.")

    else:
        print(f"Car plate {car_plate} not found in car_toll table.")
        logging.info(f"Car plate {car_plate} not found in car_toll table.")

    print("Processing completed.")
    logging.info("Processing completed.")