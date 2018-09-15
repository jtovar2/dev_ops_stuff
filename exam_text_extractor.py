import datastore_manager
from google.cloud import storage
from google.cloud import vision
import os
import textract

lcp = os.environ['LCP']
lcp = lcp.upper()
project = os.environ['PROJECT_ID']

storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()



exams_to_be_processed_kind = 'exams_to_be_processed_{LCP}'.format(LCP=lcp)

exam_dm = datastore_manager.DatastoreManager(project, exams_to_be_processed_kind, lcp=lcp)

gql_query = "SELECT * from {kind}".format(kind=exams_to_be_processed_kind)
query = exam_dm.client.query(kind=exams_to_be_processed_kind)

results = exam_dm.run_query(query)

print results

for result in results:
	blob_info = result['file'].split('/o/')
	bucket_name = blob_info[0]
	bucket = storage_client.get_bucket(bucket_name)
	blob_name = blob_info[1]

	blob = storage.blob.Blob(blob_name, bucket)
	with open(blob_name, 'wb') as file_obj:
		blob.download_to_file(file_obj)

	try:
		text = textract.process(blob_name)
		print("local**********************")
		print(text)
		print("local*******************")
	except:
		print("textract fucked up")

	'''gcp_response = vision_client.document_text_detection({'source': {'image_uri': 'gs://{bucket_name}/{blob_name}'.format(bucket_name=bucket_name, blob_name=blob_name)}})

	print("GCP****************")
	print(gcp_response.full_text_annotation.text)
	print("GCP****************")'''
