from odoo import models, fields, exceptions

class Attendance(models.Model):
  _name = 'attendance_tracking.attendance'
  _description = 'Attendance Record'
  _rec_name = 'date'

  student_id = fields.Many2one('attendance_tracking.student', string='Student', required=True)
  date = fields.Date(string='Date', required=True, default=lambda self: fields.Date.context_today(self))
  time_in = fields.Datetime(string="Time In", default=fields.Datetime.now)
  time_out = fields.Datetime(string="Time Out")
  status = fields.Selection([
    ('in_progress', 'In Progress'),
    ('complete', 'Complete'),
  ], string='Status', default='in_progress', required=True)
  time_in_image = fields.Binary(string="Time In Image", attachment=True)
  time_out_image = fields.Binary(string="Time Out Image", attachment=True)

  def action_time_in(self):
    student = self.env['attendance_tracking.student'].search([
      ('name', '=', self.env.user.partner_id.id),
    ], limit=1)
    if not student:
      raise exceptions.UserError('You are not registered as a student. Please contact an administrator.')
    today = fields.Date.context_today(self)
    existing = self.search([
      ('student_id', '=', student.id),
      ('date', '=', today),
    ], limit=1)
    if existing:
      raise exceptions.UserError('You have already timed in today.')
    new_record = self.create({'student_id': student.id})
    return {
      'type': 'ir.actions.act_window',
      'res_model': 'attendance_tracking.attendance',
      'res_id': new_record.id,
      'view_mode': 'form',
      'views': [(False, 'form')],
      'target': 'current'
    }

  def action_time_out(self):
    student = self.env['attendance_tracking.student'].search([
      ('name', '=', self.env.user.partner_id.id),
    ], limit=1)
    if not student:
      raise exceptions.UserError('You are not registered as a student. Please contact an administrator.')
    today = fields.Date.context_today(self)
    record = self.search([
      ('student_id', '=', student.id),
      ('date', '=', today),
      ('status', '=', 'in_progress'),
    ], limit=1)
    if not record:
      raise exceptions.UserError('No active attendance record found.')
    record.write({
      'time_out': fields.Datetime.now(),
      'status': 'complete',
    })
    return {
      'type': 'ir.actions.act_window',
      'res_model': 'attendance_tracking.attendance',
      'res_id': record.id,
      'view_mode': 'form',
      'views': [(False, 'form')],
      'target': 'current',
    }