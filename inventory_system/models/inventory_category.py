from odoo import fields, models

class InventoryCategory(models.Model):
  _name = "inventory.category"
  _description = "Inventory Category"

  name = fields.Char(required=True)
  product_id = fields.One2many("inventory.products", "category_id", string="Products")