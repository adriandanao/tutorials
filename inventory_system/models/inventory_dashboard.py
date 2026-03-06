from odoo import api, fields, models


class InventoryDashboard(models.Model):
  _name = "inventory.dashboard"
  _description = "Inventory Dashboard"
  _rec_name = "name"

  name = fields.Char(default="Dashboard", readonly=True)

  total_products = fields.Integer(string="Total Products", compute="_compute_stats")
  total_categories = fields.Integer(string="Total Categories", compute="_compute_stats")
  total_stock_value = fields.Float(string="Total Stock Value", compute="_compute_stats")
  total_low_stock = fields.Integer(string="Low Stock Items", compute="_compute_stats")
  total_out_of_stock = fields.Integer(string="Out of Stock Items", compute="_compute_stats")

  low_stock_product_ids = fields.Many2many(
    "inventory.products",
    relation="inventory_dashboard_low_stock_rel",
    column1="dashboard_id",
    column2="product_id",
    string="Low Stock Products",
    compute="_compute_low_stock_products",
  )

  recent_adjustment_ids = fields.Many2many(
    "inventory.adjustments",
    relation="inventory_dashboard_recent_adj_rel",
    column1="dashboard_id",
    column2="adjustment_id",
    string="Recent Adjustments",
    compute="_compute_recent_adjustments",
  )

  out_of_stock_product_ids = fields.Many2many(
    "inventory.products",
    relation="inventory_dashboard_out_of_stock_rel",
    column1="dashboard_id",
    column2="product_id",
    string="Out of Stock Products",
    compute="_compute_out_of_stock_products",
  )

  top_selling_product_ids = fields.Many2many(
    "inventory.products",
    relation="inventory_dashboard_top_selling_rel",
    column1="dashboard_id",
    column2="product_id",
    string="Top Selling Products",
    compute="_compute_top_selling_products",
  )

  @api.depends()
  def _compute_stats(self):
    Product = self.env['inventory.products']
    for record in self:
      products = Product.search([])
      record.total_products = len(products)
      
      # Compute categories if field exists
      if "category_id" in Product._fields:
        record.total_categories = len(products.mapped("category_id"))
      else:
        record.total_categories = 0
        
      # Compute stock value
      if "price" in Product._fields:
        record.total_stock_value = sum(p.stock * p.price for p in products)
      else:
        record.total_stock_value = 0.0

      # Compute low stock and out of stock counts
      if "stock" in Product._fields and "min_stock" in Product._fields:
        record.total_low_stock = len([p for p in products if 0 < p.stock <= p.min_stock])
        record.total_out_of_stock = len([p for p in products if p.stock == 0])
      else:
        record.total_low_stock = 0
        record.total_out_of_stock = 0

  @api.depends()
  def _compute_low_stock_products(self):
    Product = self.env['inventory.products']
    for record in self:
      if "stock" in Product._fields and "min_stock" in Product._fields:
        # Filter products where stock is below or equal to their min_stock
        low_stock_products = Product.search([])
        record.low_stock_product_ids = low_stock_products.filtered(
          lambda p: 0 < p.stock <= p.min_stock
        )
      else:
        record.low_stock_product_ids = Product.browse()

  @api.depends()
  def _compute_recent_adjustments(self):
    Adjustment = self.env['inventory.adjustments']
    for record in self:
      record.recent_adjustment_ids = Adjustment.search(
        [], order='date desc', limit=5
      )

  @api.depends()
  def _compute_out_of_stock_products(self):
    Product = self.env['inventory.products']
    for record in self:
      if "stock" in Product._fields:
        out_of_stock_products = Product.search([])
        record.out_of_stock_product_ids = out_of_stock_products.filtered(
          lambda p: p.stock == 0
        )

  @api.depends()
  def _compute_top_selling_products(self):
    Product = self.env['inventory.products']
    for record in self:
      record.top_selling_product_ids = Product.search(
        [('total_revenue', '>', 0)], order='total_revenue desc', limit=10
      )