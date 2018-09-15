from oauth2client.client import GoogleCredentials
from google.cloud import datastore
from os import path
from google.auth import app_engine


import time
import google.auth

class DatastoreManager(object):
    def __init__(self, project_id, kind_name, lcp=None):

        if project_id is None:
            raise Exception('Project ID Missing')
        if kind_name is None:
            raise Exception('Kind Name is Missing')

        """init for Datastore Manager
            Args:
                project_id (:obj:`str`, optional): Google Cloud Project ID which will be running these
                    Datastore commands
        """
        self.lcp = lcp
        self.client = self.create_client(project_id)
        self.kind_name = kind_name

    # [START create_client]
    # noinspection PyPackageRequirements
    def create_client(self, project_id):
        # Create client for datastore access

        credentials = None
        credentials = GoogleCredentials.get_application_default()
        credentials, project = google.auth.default()
        return datastore.Client(project_id, credentials=credentials)

    # [END create_client]

    #This encodes all strings in the entity dict to unicode
    #So that strings don't show up as random chars in the datastore web console
    def _encode_strings_to_unicode(self, update_json):
        for key in update_json:
            if isinstance(update_json[key], str):
                update_json[key] = update_json[key].decode('utf-8')

    # [START add_entity]
    def add_entity(self, update_json):
        # add new entity to kind
        complete_key = self.client.key(self.kind_name)

        self._encode_strings_to_unicode(update_json)

        entity = datastore.Entity(key=complete_key)

        entity.update(update_json)

        self.client.put(entity)

        return entity.key

    # [END add_entity]

    def delete_entity(self, entity_name):
        key = self.client.key(self.kind_name, entity_name)
        return self.client.delete(key)

    def add_entity_with_id(self, update_json):
        complete_key = None
        if 'id' in update_json:
            id = update_json['id']
            complete_key = self.client.key(self.kind_name, id)
        else:
            complete_key = self.client.key(self.kind_name)

        entity = datastore.Entity(key=complete_key)

        self._encode_strings_to_unicode(update_json)

        entity.update(update_json)

        self.client.put(entity)

        return entity.key

    def add_list_of_entities(self, list_of_entity_dicts):
        entities = []
        for entity_dict in list_of_entity_dicts:
            self._encode_strings_to_unicode(entity_dict)
            complete_key = self.client.key(self.kind_name)
            entity = datastore.Entity(key=complete_key)
            entity.update(entity_dict)
            entities.append(entity)
        self.client.put_multi(entities)

    def add_list_of_entities_with_ids(self, list_of_entity_dicts):
        entities = []


        for entity_dict in list_of_entity_dicts:
            self._encode_strings_to_unicode(entity_dict)
            complete_key = None
            if 'id' in entity_dict:
                complete_key = self.client.key(self.kind_name, entity_dict['id'])
            else:
                complete_key = self.client.key(self.kind_name)
            entity = datastore.Entity(key=complete_key)
            entity.update(entity_dict)
            entities.append(entity)

        self.client.put_multi(entities)

    # [START update_entity]
    def update_entity(self, entity_name, update_json, no_indexes=False, skip_indexes=[]):
        # update/add entity to kind
        complete_key = self.client.key(self.kind_name, entity_name)

        if no_indexes:
            fields_list = [key for key in update_json]
            entity = datastore.Entity(key=complete_key, exclude_from_indexes=fields_list)
            entity.update(update_json)
        elif skip_indexes:
            entity = datastore.Entity(key=complete_key, exclude_from_indexes=skip_indexes)
            entity.update(update_json)
        else:
            entity = datastore.Entity(key=complete_key)
            entity.update(update_json)

        retry_attempts = 0
        sleep_time = 3
        done = False

        while retry_attempts < 3 and not done:
            try:
                self.client.put(entity)
                done = True

            except Exception as e:
                time.sleep(sleep_time)

                retry_attempts += 1
                sleep_time *= retry_attempts

                if retry_attempts == 3:
                    raise e

        return entity.key

    # [END update_entity]

    # [START get_entity]
    def get_entity(self, entity_name):
        # retrieve an entity in a kind
        key = self.client.key(self.kind_name, entity_name)
        return self.client.get(key)
        # [END get_entity]

    # [START run_query]
    def run_query(self, query):
        # retrieve an entity in a kind
        return list(query.fetch())
        # [END run_query]

    def run_query_keys_only(self, query):
        query.keys_only()
        return list(query.fetch())