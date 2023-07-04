from odoo import models, fields


class TaskDoctor(models.Model):
    _name = 'task.doctor'
    _rec_name = "first_name"
    first_name = fields.Char()
    last_name = fields.Char()
    image = fields.Binary()
    patients_ids = fields.Many2many('task.patient')
