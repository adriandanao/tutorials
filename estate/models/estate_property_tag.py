from odoo import fields, models

class EstatePropertyTag(models.Model):
  _name = "estate.property.tag"
  _description = "Estate Property Tag"
  _order = "name"

  name = fields.Char(required=True)
  color = fields.Integer(string="Color Index")

  _check_name = models.Constraint(
    "UNIQUE(name)",
    "Tag names must be unique."
  )