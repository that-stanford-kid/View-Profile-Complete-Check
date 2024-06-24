import sys
import json
import requests
from ciscoisesdk import IdentityServicesEngineAPI

def authenticate_to_ise(ise_host, ise_user, ise_password):
    api = IdentityServicesEngineAPI(username=ise_user, password=ise_password, base_url=f"https://{ise_host}:9060", verify=False)
    return api

def validate_ise_updates(ise_results_file, ise_host, ise_user, ise_password):
    with open(ise_results_file, 'r') as f:
        results = json.load(f)
        
    validation_results = []
    