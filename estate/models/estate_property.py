from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class EstateProperty(models.Model):
  _name = "estate.property"
  _description = "Estate Property"
  _rec_name = "title"
  _order = "id desc"

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
  active = fields.Boolean(default=True)

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
      ('cancelled', 'Cancelled'),
    ],
    default='new'
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

  @api.onchange('garden')
  def _onchange_garden(self):
    if self.garden:
      self.garden_area = 10
      self.garden_orientation = 'north'
    else:
      self.garden_area = 0
      self.garden_orientation = ''

  def action_set_cancel(self):
    for record in self:
      if (record.status == 'sold'):
        raise UserError('You cannot cancel a sold property.')
      record.status = 'cancelled'
    return True
  
  def action_set_sell(self):
    for record in self:
      if (record.status == 'cancelled'):
        raise UserError('You cannot sell a cancelled property.')
      record.status = 'sold'
    return True
  
  _check_expected_price = models.Constraint(
    "CHECK(expected_price > 0)",
    "The expected price must be strictly positive."
  )

  _check_selling_price = models.Constraint(
    "CHECK(selling_price >= 0)",
    "The selling price cannot be negative."
  )

  @api.constrains('selling_price', 'expected_price')
  def _check_selling_price(self):
    for record in self:
      if record.selling_price and record.expected_price:
        if record.selling_price < 0.9 * record.expected_price:
          raise UserError('Selling price cannot be lower than 90% of the expected price.')