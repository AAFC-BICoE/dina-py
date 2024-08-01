class Relationship:
	def __init__(self, type, id):
		self.type = type
		self.id = id

class RelationshipDTO:
	def __init__(self):
		self.relationships = {}

	class Builder:
		def __init__(self):
			self.dto = RelationshipDTO()

		def add_relationship(self, key, type, id):
			self.dto.relationships[key] = Relationship(type, id)
			return self

		def build(self):
			return self.dto.relationships
