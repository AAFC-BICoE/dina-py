def SkipUndefinedField(base_field_class, *args, **kwargs):
	class CustomField(base_field_class):
		SKIP_MARKER = "//SKIP_FIELD_MARKER//"

		def __init__(self, *args, **kwargs):
			super(CustomField, self).__init__(*args, **kwargs)

		def _serialize(self, value, attr, obj, **kwargs):
			if isinstance(value, list):
				return [self.SKIP_MARKER if v == 'undefined' else v for v in value]
			if value == 'undefined':
				return self.SKIP_MARKER  # Return a special marker value
			return super(CustomField, self)._serialize(value, attr, obj, **kwargs)
		
		def _deserialize(self, value, attr, data, **kwargs):
			if isinstance(value, list):
				if 'undefined' in value:
					return []
				return value
			if value == 'undefined':
				return self.SKIP_MARKER  # Handle non-list 'undefined' values if needed
			return super(CustomField, self)._deserialize(value, attr, data, **kwargs)

	return CustomField(*args, **kwargs)