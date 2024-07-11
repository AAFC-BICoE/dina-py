from marshmallow_jsonapi import Schema, fields

class AttributesSchema(Schema):
    id = fields.String()
    version = fields.Integer()
    dwcCatalogNumber = fields.String()
    materialSampleName = fields.String()
    materialSampleType = fields.String()
    createdBy = fields.String()
    createdOn = fields.DateTime()
    barcode = fields.String()
    group = fields.String()
    managedAttributes = fields.Dict()
    preparationManagedAttributes = fields.Dict()
    dwcOtherCatalogNumbers = fields.List(fields.String())
    preservationType = fields.String()
    preparationFixative = fields.String()
    preparationMaterials = fields.String()
    preparationSubstrate = fields.String()
    preparationDate = fields.Date()
    preparationRemarks = fields.String()
    dwcDegreeOfEstablishment = fields.String()
    materialSampleState = fields.String()
    stateChangedOn = fields.Date()
    stateChangeRemarks = fields.String()
    materialSampleRemarks = fields.String()
    sourceSet = fields.String()
    extensionValues = fields.Dict()
    restrictionFieldsExtension = fields.Dict()
    restrictionRemarks = fields.String()
    isRestricted = fields.Boolean()
    materialSampleChildren = fields.List(fields.Raw())
    associations = fields.List(fields.Raw())
    tags = fields.List(fields.String())
    publiclyReleasable = fields.Boolean()
    notPubliclyReleasableReason = fields.String()
    hostOrganism = fields.Dict()
    scheduledActions = fields.List(fields.Raw())
    hierarchy = fields.List(fields.Raw())
    allowDuplicateName = fields.Boolean()
    # Additional fields
    type = fields.String()
    collectingEvent = fields.String()
    collection = fields.String()
    materialSampleRemarks = fields.String()
    createdOn = fields.DateTime()
    preservationType = fields.String()
    materialSampleChildren = fields.List(fields.Raw())
    notPubliclyReleasableReason = fields.String()
    associations = fields.List(fields.Raw())
    restrictionRemarks = fields.String()
    preparationRemarks = fields.String()
    materialSampleState = fields.String()
    preparationSubstrate = fields.String()
    dwcOtherCatalogNumbers = fields.List(fields.String())
    createdBy = fields.String()
    preparationDate = fields.Date()
    version = fields.Integer()
    barcode = fields.String()
    allowDuplicateName = fields.Boolean()
    stateChangeRemarks = fields.String()
    dwcCatalogNumber = fields.String()
    stateChangedOn = fields.Date()
    dwcDegreeOfEstablishment = fields.String()
    tags = fields.List(fields.String())
    sourceSet = fields.String()
    preparationMaterials = fields.String()
    materialSampleName = fields.String()
    extensionValues = fields.Dict()
    group = fields.String()
    preparationManagedAttributes = fields.Dict()

    class Meta:
        type_ = "attributes"
        strict = False