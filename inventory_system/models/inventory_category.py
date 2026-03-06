from odoo import api, fields, models

class InventoryCategory(models.Model):
  _name = "inventory.category"
  _description = "Inventory Category"
  _order = "name asc"

  name = fields.Char(required=True)
  product_id = fields.One2many("inventory.products", "category_id", string="Products")
  product_count = fields.Integer(string="No. of Products", compute="_compute_product_count")

  @api.depends("product_id")
  def _compute_product_count(self):
    for record in self:
      record.product_count = len(record.product_id)