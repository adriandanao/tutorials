from odoo import models, fields

class Movie(models.Model):
  _name = "movie_listings.movie"
  _description = "Movie Information"
  _rec_name = "title"

  title = fields.Char(string="Title", required=True)
  synopsis = fields.Text(string="Synopsis")
  screening_start = fields.Date(string="Screening Start Date")
  screening_end = fields.Date(string="Screening End Date")