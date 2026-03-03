from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
  _name = "estate.property.offer"
  _description = "Estate Property Offer"
  _order = "price desc"

  price = fields.Float()
  status = fields.Selection(
    string='Status',
    selection=[
      ('accepted', 'Accepted'),
      ('refused', 'Refused'),
      ('pending', 'Pending'),
    ],
    default='pending'
  )
  partner_id = fields.Many2one("res.partner", string="Partner", required=True)
  property_id = fields.Many2one("estate.property", string="Property", required=True)
  validity = fields.Integer(string="Validity (days)", default=7)
  date_deadline = fields.Date(
    compute="_compute_date_deadline",
    string="Deadline",
    inverse="_inverse_date_deadline",
    store=True
  )

  @api.depends('validity', 'create_date')
  def _compute_date_deadline(self):
    for record in self:
      if record.create_date and record.validity:
        create_dt = fields.Datetime.from_string(record.create_date)
        deadline_dt = create_dt + relativedelta(days=record.validity)
        record.date_deadline = deadline_dt.date()
      else:
        record.date_deadline = False

  def _inverse_date_deadline(self):
    for record in self:
      if record.date_deadline and record.create_date:
        create_dt = fields.Datetime.from_string(record.create_date)
        delta = record.date_deadline - create_dt.date()
        record.validity = delta.days

  def write(self, vals):
    if 'status' in vals:
      for record in self:
        if record.status and record.status != 'pending' and vals.get('status') != record.status:
          raise UserError('You cannot change the status of an offer that has already been set.')
    return super().write(vals)

  def action_accept_offer(self):
    for record in self:
      # ensure no other accepted offer exists for this property
      other = record.property_id.offer_ids.filtered(lambda o: o.status == 'accepted' and o.id != record.id)
      if other:
        raise UserError('There is already an accepted offer for this property.')
      record.status = 'accepted'
      record.property_id.selling_price = record.price
    return True
  
  def action_refuse_offer(self):
    for record in self:
      record.status = 'refused'
    return True
  
  _check_offer_price = models.Constraint(
    "CHECK(price > 0)",
    "The offer price must be strictly positive."
  )