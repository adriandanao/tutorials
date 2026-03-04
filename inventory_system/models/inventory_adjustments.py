from odoo import fields, models

class InventoryAdjustments(models.Model):
  _name = "inventory.adjustments"
  _description = "Inventory Adjustments"

  # use singular form for the Many2one field and match in views/relations
  product_id = fields.Many2one("inventory.products", string="Product", required=True)
  type = fields.Selection(
    string="Type",
    selection=[
      ('incoming', 'Incoming'),
      ('outgoing', 'Outgoing'),
    ]
  )
  units = fields.Integer(required=True)
  reason = fields.Text()
  date = fields.Datetime(default=fields.Datetime.now)

  def create(self, vals_list):
    records = super().create(vals_list)
    for record in records:
      if record.type == 'incoming':
        record.product_id.stock += record.units
        record.product_id.last_restocked = record.date
      elif record.type == 'outgoing':
        record.product_id.stock -= record.units
    return records