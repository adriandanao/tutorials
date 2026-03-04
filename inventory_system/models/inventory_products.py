from odoo import fields, models, api

class InventoryProducts(models.Model):
  _name = "inventory.products"
  _description = "Inventory Products"
  _rec_name = "product_name"

  product_name = fields.Char(required=True)
  sku_number = fields.Char(required=True)
  category_id = fields.Many2one("inventory.category", string="Category")
  stock = fields.Integer(default=0)
  price = fields.Float(required=True)
  status = fields.Selection(
    string="Status",
    selection=[
      ('in_stock', 'In Stock'),
      ('out_of_stock', 'Out of Stock'),
      ('low_stock', 'Low Stock'),
    ],
    default='in_stock',
    compute="_compute_status",
    store=True
  )
  description = fields.Text()
  supplier = fields.Char()
  location = fields.Char()
  min_stock = fields.Integer(default=10)
  last_restocked = fields.Datetime(store=True)
  user_id = fields.Many2one("res.users", string="User")
  adjustment_ids = fields.One2many("inventory.adjustments", "product_id", string="Adjustments")
  recent_adjustment_ids = fields.One2many("inventory.adjustments", "product_id", compute="_compute_recent_adjustments", string="Recent Adjustments")
  last_adjustment_id = fields.Many2one("inventory.adjustments", compute="_compute_recent_adjustments", string="Last Adjustment")

  def _compute_recent_adjustments(self):
    for product in self:
      recent = self.env['inventory.adjustments'].search([("product_id", "=", product.id)],order="date desc", limit=5)
      product.recent_adjustment_ids = recent
      product.last_adjustment_id = recent[:1] if recent else False

  @api.depends('stock', 'min_stock')
  def _compute_status(self):
    for product in self:
      if product.stock <= 0:
        product.status = 'out_of_stock'
      elif product.stock <= product.min_stock:
        product.status = 'low_stock'
      else:
        product.status = 'in_stock'