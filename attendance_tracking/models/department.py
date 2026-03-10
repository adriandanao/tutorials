from odoo import models, fields

class Department(models.Model):
  _name = "attendance_tracking.department"
  _description = "Department Information"
  _rec_name = "title"

  title = fields.Char(string="Title", required=True)
  student_id = fields.One2many('attendance_tracking.student', 'department_id', string="Students", required=True)