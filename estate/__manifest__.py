{
    'name': "Estate",
    'version': '1.0',
    'summary': "Manage your real estate properties",
    'category': 'Real Estate',
    'depends': ['base'],
    'author': "Adrian",
    'application': True,
    'installable': True,
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
    ],
}