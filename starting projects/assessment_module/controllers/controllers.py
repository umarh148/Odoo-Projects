# -*- coding: utf-8 -*-
# from odoo import http


# class AssessmentModule(http.Controller):
#     @http.route('/assessment_module/assessment_module', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/assessment_module/assessment_module/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('assessment_module.listing', {
#             'root': '/assessment_module/assessment_module',
#             'objects': http.request.env['assessment_module.assessment_module'].search([]),
#         })

#     @http.route('/assessment_module/assessment_module/objects/<model("assessment_module.assessment_module"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('assessment_module.object', {
#             'object': obj
#         })
