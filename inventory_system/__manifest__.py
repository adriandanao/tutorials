{
  'name': 'Inventory System',
  'version': '1.0',
  'summary': 'Manage your inventory and stock levels',
  'category': 'Inventory',
  'depends': ['base'],
  'author': 'Adrian',
  'application': True,
  'installable': True,
  'data': [
    'security/ir.model.access.csv',
    'views/inventory_dashboard_views.xml',
    'views/inventory_products_views.xml',
    'views/inventory_category_views.xml',
  ]
}