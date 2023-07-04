from odoo import models, fields


class TaskDepartement(models.Model):
    _name = 'task.departement'
    name = fields.Char()
    capacity = fields.Integer()
    is_open = fields.Boolean()
    patient_ids = fields.One2many('task.patient', 'departement_id')
