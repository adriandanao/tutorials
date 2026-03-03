from odoo import fields, models

class EstatePropertyType(models.Model):
  _name = "estate.property.type"
  _description = "Estate Property Type"
  _order = "name"
  
  name = fields.Char(required=True)
  property_ids = fields.One2many("estate.property", "property_type_id", string="Properties")

  _check_name = models.Constraint(
    "UNIQUE(name)",
    "Property type names must be unique."
  )