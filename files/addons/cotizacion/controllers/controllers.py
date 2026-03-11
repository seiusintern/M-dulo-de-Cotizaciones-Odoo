# -*- coding: utf-8 -*-
# from odoo import http


# class Cotizacion(http.Controller):
#     @http.route('/cotizacion/cotizacion', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cotizacion/cotizacion/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cotizacion.listing', {
#             'root': '/cotizacion/cotizacion',
#             'objects': http.request.env['cotizacion.cotizacion'].search([]),
#         })

#     @http.route('/cotizacion/cotizacion/objects/<model("cotizacion.cotizacion"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cotizacion.object', {
#             'object': obj
#         })

