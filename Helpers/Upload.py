#!/usr/bin/env python3

import requests
from requests.auth import HTTPBasicAuth

class Upload:
	def __init__(self: object) -> None:
		self.password = '1nt3GraTi0n'
		self.headers={'content-type': 'text/plain'}
		self.encoding = 'utf-8-sig'
		self.is_org = False
		self.delete = False

	def upload(self: object):
		if not self.payload or not self.username:
			raise UploadError("Missing payload or username")
		else:
			response = requests.post(self.endpoint, headers=self.headers, data=self.payload, auth=HTTPBasicAuth(self.username, self.password))

	@property
	def payload(self: object) -> str:
		return self._payload.encode(self.encoding)

	@payload.setter
	def payload(self: object, unformatted_payload: list) -> None:
		formatted_payload = self.header
		formatted_payload = f"{formatted_payload}\n{unformatted_payload}"
		self._payload = formatted_payload
	
