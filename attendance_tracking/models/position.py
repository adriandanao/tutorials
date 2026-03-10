from odoo import models, fields

class Position(models.Model):
  _name = "attendance_tracking.position"
  _description = "Position Information"
  _rec_name = "title"

  title = fields.Char(string="Title", required=True)
  student_id = fields.One2many('attendance_tracking.student', 'position_id', string="Students", required=True)