from __future__ import unicode_literals

class SocketResponseMessage(object):

	def __init__(self, uuid, rtype, sender=None, receiver=None, status, message=None, args=None, data=None):
		self.uuid = uuid
		self.type = rtype
		self.sender = sender
		self.receiver = receiver
		self.status = status
		self.message = message
		self.args = args
		self.data = data


	def to_json(self):
		return {
			'uuid': self.uuid,
			'type': self.type,
			'sender': self.sender,
			'receiver': self.receiver,
			'status': self.status,
			'message': self.message,
			'args': self.args,
			'data': self.data
		}