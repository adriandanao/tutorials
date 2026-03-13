{
  'name': 'Inventory System',
  'version': '1.0',
  'summary': 'Manage your inventory and stock levels',
  'category': 'Inventory',
  'depends': ['base', 'web', 'board'],
  'author': 'Adrian',
  'application': True,
  'installable': True,
  'data': [
    'security/ir.model.access.csv',
    'data/dashboard_data.xml',
    'views/dashboard_views.xml',
    'views/inventory_products_views.xml',
    'views/inventory_category_views.xml',
    'views/inventory_adjustments_views.xml',
    'views/assets.xml',
  ],
  'assets': {
    'web.assets_backend': [
      'inventory_system/static/src/css/styles.css',
    ],
  }
}