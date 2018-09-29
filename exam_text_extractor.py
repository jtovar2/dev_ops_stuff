import datastore_manager
from google.cloud import storage
from google.cloud import vision
from google.cloud import vision_v1p3beta1 as handwriting_vision
import os
import textract
import requests

lcp = os.environ['LCP']
lcp = lcp.upper()
project = os.environ['PROJECT_ID']

#app_hostname = os.environ['APP_HOSTNAME']
app_hostname = "{lcp}-exambae-"
app_hostname = app_hostname.format(lcp=lcp)

insert_document_endpoint = 'http://{app_hostname}/document/insert'.format(app_hostname=app_hostname)

storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()
handwriting_client = handwriting_vision.ImageAnnotatorClient()

handwriting_image = handwriting_vision.types.Image()
handwriting_imagesource.image_uri = uri

exams_to_be_processed_kind = 'exams_to_be_processed_{LCP}'.format(LCP=lcp)

exam_dm = datastore_manager.DatastoreManager(project, exams_to_be_processed_kind, lcp=lcp)

gql_query = "SELECT * from {kind}".format(kind=exams_to_be_processed_kind)
query = exam_dm.client.query(kind=exams_to_be_processed_kind)

results = exam_dm.run_query(query)

print results


jsont_dicts = []

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
		print("local*******************")
	except:
		print("textract fucked up")

	gcp_response = vision_client.document_text_detection({'source': {'image_uri': 'gs://{bucket_name}/{blob_name}'.format(bucket_name=bucket_name, blob_name=blob_name)}})
	handwriting_image = handwriting_vision.types.Image()
	handwriting_image.source.image_uri = blob.media_link()
	
	handWriting_image_context = handwriting_vision.types.ImageContext(
        language_hints=['en-t-i0-handwrit'])
	
	
	
	handwriting_response = handwriting_client.document_text_detection(image=handwriting_image,
                                              image_context=handWriting_image_context)
	
	print("GCP****************")
	print(gcp_response.full_text_annotation.text)
	print("GCP****************")


	if (gcp_response.full_text_annotation.text is not None and gcp_response.full_text_annotation.text != "") or ( local_text is not None and local_text != "")
	or ( handwriting_response is not None and handwriting_response != ""):

		gcp_text = gcp_response.full_text_annotation.text
		
		handwriting_text = handwriting_response.full_text_annotation.text
		json_dict = {}
		json_dict['school'] = result['school']
		json_dict['description'] = result['description']
		json_dict['school_class'] = result['school_class']
		json_dict['local_text'] = local_text
		json_dict['gcp_text'] = gcp_text
		json_dict['handwriting_text'] = handwriting_text
		json_dict['id'] = str(result.key.id_oresult)

		jsont_dicts.append(json_dict)

	

#response = requests.post(insert_document_endpoint, data=json.dumps(json_dict) )
print("the dictionary ")
print("the dictionary ")
print("the dictionary ")
print(jsont_dicts)

json_dict  = {}
json_dict['entities'] = json_dicts




