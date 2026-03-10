from odoo import api, fields, models
from datetime import date, datetime, timedelta
import pytz

class Dashboard(models.Model):
  _name = "attendance_tracking.dashboard"
  _description = "Attendance Dashboard"
  _rec_name = "name"

  name = fields.Char(default="Dashboard", readonly=True)

  currently_present = fields.Integer(string="Currently Present", compute="_compute_students")
  total_attendance_records = fields.Integer(string="Total Attendance Records Today", compute="_compute_attendance_records")
  total_absent_today = fields.Integer(string="Absent Today", compute="_compute_attendance_records")
  total_completed_today = fields.Integer(string="Completed Today", compute="_compute_attendance_records")
  attendance_percentage = fields.Float(string="Today's Attendance %", compute="_compute_attendance_percentage")
  weekly_attendance_percentage = fields.Float(string="Weekly Attendance %", compute="_compute_weekly")
  monthly_attendance_percentage = fields.Float(string="Monthly Attendance %", compute="_compute_monthly")
  average_time_in = fields.Char(string="Average Time In", compute="_compute_time_stats")
  late_count = fields.Integer(string="Late Arrivals Today", compute="_compute_time_stats")

  @api.model
  def get_dashboard_data(self):
    today = fields.Date.context_today(self)
    total_students = self.env['attendance_tracking.student'].search_count([])
    today_records = self.env['attendance_tracking.attendance'].search([('date', '=', today)])
    currently_present = len(today_records.filtered(lambda r: r.status == 'in_progress'))
    total_completed = len(today_records.filtered(lambda r: r.status == 'complete'))
    total_present_today = len(today_records)
    total_absent = total_students - total_present_today
    attendance_pct = (total_present_today / total_students * 100) if total_students else 0.0

    # Last 7 days data for chart
    weekly_data = []
    daily_pcts = []
    for i in range(6, -1, -1):
      day = today - timedelta(days=i)
      count = self.env['attendance_tracking.attendance'].search_count([('date', '=', day)])
      pct = (count / total_students * 100) if total_students else 0.0
      daily_pcts.append(pct)
      weekly_data.append({
        'date': day.strftime('%a %m/%d'),
        'present': count,
        'percentage': round(pct, 1),
      })
    weekly_pct = sum(daily_pcts) / 7 if daily_pcts else 0.0

    # Monthly average
    first_day = today.replace(day=1)
    days_so_far = (today - first_day).days + 1
    monthly_total = 0.0
    for i in range(days_so_far):
      day = first_day + timedelta(days=i)
      count = self.env['attendance_tracking.attendance'].search_count([('date', '=', day)])
      monthly_total += (count / total_students * 100) if total_students else 0.0
    monthly_pct = monthly_total / days_so_far if days_so_far else 0.0

    # Time stats
    time_records = today_records.filtered(lambda r: r.time_in)
    avg_time_in = 'N/A'
    late_count = 0
    CUTOFF_HOUR = 8
    if time_records:
      user_tz = pytz.timezone(self.env.user.tz or 'UTC')
      def to_local(dt):
        return pytz.utc.localize(dt).astimezone(user_tz)
      total_seconds = sum(
        to_local(r.time_in).hour * 3600 + to_local(r.time_in).minute * 60 + to_local(r.time_in).second
        for r in time_records
      )
      avg_s = total_seconds // len(time_records)
      avg_h = avg_s // 3600
      avg_m = (avg_s % 3600) // 60
      period = "AM" if avg_h < 12 else "PM"
      avg_h12 = avg_h % 12 or 12
      avg_time_in = f"{avg_h12:02d}:{avg_m:02d} {period}"
      late_count = len(time_records.filtered(
        lambda r: to_local(r.time_in).hour > CUTOFF_HOUR or
                  (to_local(r.time_in).hour == CUTOFF_HOUR and to_local(r.time_in).minute > 0)
      ))

    return {
      'total_students': total_students,
      'currently_present': currently_present,
      'total_completed_today': total_completed,
      'total_absent_today': total_absent,
      'attendance_percentage': round(attendance_pct, 1),
      'weekly_attendance_percentage': round(weekly_pct, 1),
      'monthly_attendance_percentage': round(monthly_pct, 1),
      'average_time_in': avg_time_in,
      'late_count': late_count,
      'weekly_data': weekly_data,
    }

  @api.depends()
  def _compute_students(self):
    for rec in self:
      today = fields.Date.today()
      rec.total_students = self.env['attendance_tracking.student'].search_count([])
      rec.currently_present = self.env['attendance_tracking.attendance'].search_count([
        ('date', '=', today),
        ('status', '=', 'in_progress'),
      ])

  @api.depends()
  def _compute_attendance_records(self):
    for rec in self:
      today = fields.Date.today()
      all_today = self.env['attendance_tracking.attendance'].search([('date', '=', today)])
      total_students = self.env['attendance_tracking.student'].search_count([])
      rec.total_attendance_records = len(all_today)
      rec.total_absent_today = total_students - len(all_today)
      rec.total_completed_today = len(all_today.filtered(lambda r: r.status == 'complete'))

  @api.depends()
  def _compute_attendance_percentage(self):
    for rec in self:
      today = fields.Date.today()
      total = self.env['attendance_tracking.student'].search_count([])
      present = self.env['attendance_tracking.attendance'].search_count([('date', '=', today)])
      rec.attendance_percentage = (present / total * 100) if total else 0.0

  @api.depends()
  def _compute_weekly(self):
    for rec in self:
      today = fields.Date.today()
      total_students = self.env['attendance_tracking.student'].search_count([])
      if not total_students:
        rec.weekly_attendance_percentage = 0.0
        continue
      daily_pcts = []
      for i in range(7):
        day = today - timedelta(days=i)
        count = self.env['attendance_tracking.attendance'].search_count([('date', '=', day)])
        daily_pcts.append(count / total_students * 100)
      rec.weekly_attendance_percentage = sum(daily_pcts) / 7

  @api.depends()
  def _compute_monthly(self):
    for rec in self:
      today = fields.Date.today()
      total_students = self.env['attendance_tracking.student'].search_count([])
      if not total_students:
        rec.monthly_attendance_percentage = 0.0
        continue
      first_day = today.replace(day=1)
      days_so_far = (today - first_day).days + 1
      daily_pcts = []
      for i in range(days_so_far):
        day = first_day + timedelta(days=i)
        count = self.env['attendance_tracking.attendance'].search_count([('date', '=', day)])
        daily_pcts.append(count / total_students * 100)
      rec.monthly_attendance_percentage = sum(daily_pcts) / days_so_far

  @api.depends()
  def _compute_time_stats(self):
    CUTOFF_HOUR = 8  # students arriving after 8:00 AM are considered late
    for rec in self:
      today = fields.Date.today()
      records = self.env['attendance_tracking.attendance'].search([
        ('date', '=', today),
        ('time_in', '!=', False),
      ])
      if not records:
        rec.average_time_in = 'N/A'
        rec.late_count = 0
        continue
      user_tz = pytz.timezone(self.env.user.tz or 'UTC')
      def to_local(dt):
        return pytz.utc.localize(dt).astimezone(user_tz)
      total_seconds = sum(
        to_local(r.time_in).hour * 3600 + to_local(r.time_in).minute * 60 + to_local(r.time_in).second
        for r in records
      )
      avg_seconds = total_seconds // len(records)
      avg_h = avg_seconds // 3600
      avg_m = (avg_seconds % 3600) // 60
      period = "AM" if avg_h < 12 else "PM"
      avg_h12 = avg_h % 12 or 12
      rec.average_time_in = f"{avg_h12:02d}:{avg_m:02d} {period}"
      rec.late_count = len(records.filtered(
        lambda r: to_local(r.time_in).hour > CUTOFF_HOUR or
                  (to_local(r.time_in).hour == CUTOFF_HOUR and to_local(r.time_in).minute > 0)
      ))
