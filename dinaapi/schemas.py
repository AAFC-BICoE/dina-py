from marshmallow_jsonapi import Schema, fields


class IdentifierSchema(Schema):
    class Meta:
        type_ = "identifier"

    id = fields.Str(required=True)


class OrganizationSchema(Schema):
    class Meta:
        type_ = "organization"

    id = fields.Str(required=True)


class PersonSchema(Schema):
    class Meta:
        type_ = "person"
        self_view = "/api/v1/person/{id}"
        # self_view_many = "person_list"

    id = fields.Str(required=True)
    displayName = fields.Str(required=True, attribute="displayName")
    email = fields.Email(required=True, attribute="email")
    createdBy = fields.Str(required=True, attribute="createdBy")
    createdOn = fields.DateTime(required=True, attribute="createdOn")
    givenNames = fields.Str(required=True, attribute="givenNames")
    familyNames = fields.Str(required=True, attribute="familyNames")
    webpage = fields.Url(required=True, attribute="webpage")
    remarks = fields.Str(required=True, attribute="remarks")
    aliases = fields.List(fields.Str(), required=True, attribute="aliases")

    # Define relationships using .nested
    organizations = fields.Relationship(
        type_="organization",
        attribute="organizations",
        many=True,
        include_resource_linkage=True,
        nested="OrganizationSchema",
    )
    identifiers = fields.Relationship(
        type_="identifier",
        attribute="identifiers",
        many=True,
        include_resource_linkage=True,
        nested="IdentifierSchema",
    )
