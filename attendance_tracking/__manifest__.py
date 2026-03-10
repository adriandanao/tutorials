{
  'name': 'Attendance Tracking',
  'version': '1.0',
  'summary': 'Track student attendance and generate reports',
  'category': 'Education',
  'depends': ['base', 'web', 'board'],
  'author': 'Adrian',
  'application': True,
  'installable': True,
  'data': [
    'security/ir.model.access.csv',
    'views/dashboard.xml',
    'views/attendance.xml',
    'views/student.xml',
    'views/department.xml',
  ],
  'assets': {
    'web.assets_backend': [
      'attendance_tracking/static/src/dashboard/dashboard.xml',
      'attendance_tracking/static/src/dashboard/dashboard.js',

      'attendance_tracking/static/src/webcam/webcam_widget.xml',
      'attendance_tracking/static/src/webcam/webcam_widget.js'
    ]
  }
}