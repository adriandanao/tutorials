from odoo import models, fields

class Student(models.Model):
  _name = 'attendance_tracking.student'
  _description = 'Student Information'
  _rec_name = 'name'

  name = fields.Many2one('res.partner', string="Name", required=True, default=lambda self: self.env.user.partner_id.id)
  student_id = fields.Char(string="Student ID", required=True)
  email = fields.Char(string="Email")
  department_id = fields.Many2one('attendance_tracking.department', string="Department", required=True)
  position_id = fields.Many2one('attendance_tracking.position', string="Position", required=True)
  attendance_ids = fields.One2many('attendance_tracking.attendance', 'student_id', string="Attendance Records")

  _sql_constraints = [
    ('student_id_unique', 'UNIQUE(student_id)', 'A student with this ID already exists.'),
  ]
