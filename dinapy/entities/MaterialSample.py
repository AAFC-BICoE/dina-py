class MaterialSample:
    def __init__(self, id = None, type = None, attributes = None, relationships = None):
        self.id = id
        self.type = type
        self.attributes = attributes or {}
        self.relationships = relationships or {}

class MaterialSampleBuilder:
    def __init__(self):
        self.material_sample = MaterialSample(
            type=None,
            attributes=None,
            relationships=None
        )

    def set_type(self, type):
        self.material_sample.type = type
        return self

    def set_attributes(self, attributes):
        self.material_sample.attributes = attributes
        return self

    def set_relationships(self, relationships):
        self.material_sample.relationships = relationships
        return self

    def build(self):
        return self.material_sample
    
# Example usage:
builder = MaterialSampleBuilder()
sample = builder.build()
