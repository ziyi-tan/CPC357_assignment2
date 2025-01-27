# Demo Function for Highway ETC System
This code repository consists of two files that need to be included in the cloud run <ins>**demo**</ins> function: 
* `main.py`
* `requirements.txt`

### Cloud Function Main Code
The `main.py` script simulates the core functionality of a Highway Electronic Toll Collection (ETC) system. 

### Environment settings
The `requirements.txt` specifies the dependencies needed for the project to run. <br>
These dependencies will be installed by pip when setting up the project environment, ensuring that the correct versions of libraries are used.

* `functions-framework` specifies the Google Cloud Functions Framework
  * enables to deploy demo function to Google Cloud  
* `google-cloud-storage` is the Python client library for Google Cloud Storage
  * to interact with Google Cloud Storage buckets (e.g., uploading, downloading, or managing files)
* `google-cloud-vision` is the Python client library for Google Cloud Vision
  * provides tools to work with Vision API
* `google-cloud-bigquery` is the Python client library for Google Cloud BigQuery
  * to interact with BigQuery


