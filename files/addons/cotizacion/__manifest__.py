{
    'name': 'Cotizaciones Tecnicas',
    'version': '1.0',
    'depends': ['base','sale','product'],
    'data': [
        'security/ir.model.access.csv',
        'views/cotizacion_views.xml',
	'views/cotizacion_menu.xml',
    ],
    'installable': True,
    'application': True,
}
