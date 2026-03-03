from odoo import fields, models, api
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
  _name = "estate.property"
  _description = "Estate Property"
  _rec_name = "title"

  title = fields.Char(required=True)
  description = fields.Text()
  postcode = fields.Char()
  expected_price = fields.Float(required=True)
  bedrooms = fields.Integer(default=2)
  facades = fields.Integer()
  garden = fields.Boolean()
  garden_orientation = fields.Selection(
    string='Type',
    selection=[
      ('north', 'North'),
      ('south', 'South'),
      ('east', 'East'),
      ('west', 'West'),
    ]
  )
  active = fields.Boolean(default=False)

  date_availability = fields.Date(default=lambda self: fields.Date.today() + relativedelta(months=3))
  selling_price = fields.Float()
  living_area = fields.Integer()
  garage = fields.Boolean()
  garden_area = fields.Integer()
  status = fields.Selection(
    string='Type',
    selection=[
      ('new', 'New'),
      ('offer_received', 'Offer Received'),
      ('offer_accepted', 'Offer Accepted'),
      ('sold', 'Sold'),
    ]
  )
  last_seen = fields.Datetime()
  property_type_id = fields.Many2one("estate.property.type", string="Property Type")
  salesman = fields.Many2one("res.users", string="Salesman")
  buyer = fields.Many2one("res.partner", string="Buyer", default=lambda self: self.env.user.name)
  tag_ids = fields.Many2many("estate.property.tag", string="Tags")
  offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
  total_area = fields.Integer(compute="_compute_total_area", string="Total Area")
  best_offer = fields.Float(compute="_compute_best_offer", string="Best Offer")

  @api.depends('living_area', 'garden_area')
  def _compute_total_area(self):
    for record in self:
      record.total_area = record.living_area + record.garden_area

  @api.depends('offer_ids.price')
  def _compute_best_offer(self):
    for record in self:
      if record.offer_ids:
        record.best_offer = max(record.offer_ids.mapped('price'))
      else:
        record.best_offer = 0.0