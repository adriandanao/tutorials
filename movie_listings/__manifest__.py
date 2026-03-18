{
  'name': 'Movie Listings',
  'version': '1.0',
  'summary': 'Manage and display movie listings',
  'category': 'Entertainment',
  'depends': ['base', 'web'],
  'author': 'Adrian',
  'application': True,
  'installable': True,
  'data': [
    'security/ir.model.access.csv',
    'views/Movie/movie_root.xml',
    'views/Movie/movie_tree.xml',
    'views/Movie/movie_form.xml',
  ]
}