import datastore_manager
from google.cloud import storage
from google.cloud import vision
import os
import textract
import requests
import json

lcp = os.environ['LCP']
lcp = lcp.upper()
project = os.environ['PROJECT_ID']

#app_hostname = os.environ['APP_HOSTNAME']
app_hostname = "{lcp}-exambae-backend-dot-demolisherapp.appspot.com"
app_hostname = app_hostname.format(lcp=lcp)

insert_document_endpoint = 'http://{app_hostname}/document/insert'.format(app_hostname=app_hostname)

storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()


exams_to_be_processed_kind = 'exams_to_be_processed_{LCP}'.format(LCP=lcp)

exam_dm = datastore_manager.DatastoreManager(project, exams_to_be_processed_kind, lcp=lcp)

gql_query = "SELECT * from {kind}".format(kind=exams_to_be_processed_kind)
query = exam_dm.client.query(kind=exams_to_be_processed_kind)

results = exam_dm.run_query(query)

print results


json_dicts = []

for result in results:
	blob_info = result['file'].split('/o/')
	bucket_name = blob_info[0]
	bucket = storage_client.get_bucket(bucket_name)
	blob_name = blob_info[1]

	blob = storage.blob.Blob(blob_name, bucket)
	with open(blob_name, 'wb') as file_obj:
		blob.download_to_file(file_obj)

	local_text = None
	try:
		text = textract.process(blob_name)
		print("local**********************")
		print(text)
		local_text = text
                local_text = local_text.replace('\f', '').replace('\n', '')

		print("local*******************")
	except:
		print("textract fucked up")

	gcp_document_text_response = vision_client.document_text_detection({'source': {'image_uri': 'gs://{bucket_name}/{blob_name}'.format(bucket_name=bucket_name, blob_name=blob_name)}})
	image = vision.types.Image()
	image.source.image_uri = 'gs://{bucket_name}/{blob_name}'.format(bucket_name=bucket_name, blob_name=blob_name)
	
	handWriting_image_context = vision.types.ImageContext(
        language_hints=['en-t-i0-handwrit'])


	gcp_text_response = vision_client.text_detection(image=image)
	
	
	
	gcp_handwriting_response = vision_client.document_text_detection(image=image,
                                              image_context=handWriting_image_context)
	
	print("GCP****************")
	print(gcp_document_text_response.full_text_annotation.text)
	print("GCP****************")


	if (gcp_document_text_response.full_text_annotation.text is not None and gcp_document_text_response.full_text_annotation.text != "") or ( local_text is not None and local_text != "") or ( gcp_handwriting_response is not None and gcp_handwriting_response != "") or ( gcp_text_response is not None and gcp_text_response != ""):

		gcp_document_text = gcp_document_text_response.full_text_annotation.text.encode('ascii', 'ignore')
		
		gcp_handwriting_text = gcp_handwriting_response.full_text_annotation.text.encode('ascii', 'ignore')
		gcp_text = gcp_handwriting_response.full_text_annotation.text.encode('ascii', 'ignore')
		json_dict = {}
		json_dict['school'] = result['school']
		json_dict['description'] = result['description']
		json_dict['school_class'] = result['school_class']
		json_dict['local_text'] = local_text
		json_dict['gcp_document_text'] = gcp_document_text
		json_dict['gcp_handwriting_text'] = gcp_handwriting_text
		json_dict['gcp_text'] = gcp_text
		json_dict['id'] = str(result.key.id_or_name)

		json_dicts.append(json_dict)

	

print("the dictionary ")
print("the dictionary ")
print("the dictionary ")
print(json_dicts)


json_dict  = {}
json_dict['entities'] = json_dicts

if len(json_dicts) > 0:
	response = requests.post(insert_document_endpoint, data=json.dumps(json_dict) )

	print response


