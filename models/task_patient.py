import datetime

from odoo import models, fields, api
from odoo.exceptions import UserError


class TaskPatient(models.Model):
    _name = 'task.patient'
    _rec_name = 'first_name'

    first_name = fields.Char(required=True)
    last_name = fields.Char()
    email = fields.Char()
    birth_date = fields.Date()
    age = fields.Integer(compute='Calc_age')
    history = fields.Html()
    cr_ratio = fields.Float()
    blood_type = fields.Selection([("o", "O"), ("a", "A"), ("a-", "A-")])
    pcr = fields.Boolean()
    image = fields.Binary()
    Address = fields.Text()
    departement_id = fields.Many2one('task.departement')
    doctors_ids = fields.Many2many('task.doctor')
    patient_history_ids = fields.One2many('patient_history_line', 'patient_id')
    departement_capacity = fields.Integer(related='departement_id.capacity')
    state = fields.Selection([
        ('none', 'None'),
        ('undetermined', 'Undetermined'),
        ('fair', 'Fair'),
        ('serious', 'Serious'),
        ('good', 'Good')
    ], default='none')

    @api.depends('birth_date')
    def Calc_age(self):
        for rec in self:
            if rec.birth_date:
                rec.age = int((datetime.date.today() - rec.birth_date).days) / 365
            else:
                rec.age = 0

    def log_history(self):
        self.env['patient_history_line'].create(
            {
                "description": f" state changed to {self.state}",
                "patient_id": self.id
            }
        )

    def ChangeState(self):
        if self.state == 'none':
            self.state = 'undetermined'
            self.log_history()
        elif self.state == 'undetermined':
            self.state = 'fair'
            self.log_history()
        elif self.state in ['serious', 'good']:
            self.state = 'none'
            self.log_history()

    def SetSerious(self):
        if self.state == 'fair':
            self.state = 'serious'
            self.log_history()

    def SetGood(self):
        if self.state == 'fair':
            self.state = 'good'
            self.log_history()

    @api.model
    def create(self, vals):
        name_split = vals['first_name'].split()
        name_split_2 = vals['last_name'].split()
        vals['email'] = f"{name_split[0][0]}{name_split_2[0]}@gmail.com"
        unique_email = self.search([('email', '=', vals['email'])])
        if unique_email is False:
            raise UserError('Email Already Exist')
        return super().create(vals)

    def write(self, vals):
        if "first_name" and "last_name" in vals:
            for record in self:
                name_split = record.first_name.split()
                name_split_2 = record.last_name.split()
                vals['email'] = f"{name_split[0][0]}{name_split_2[0]}@gmail.com"
        super().write(vals)

    _sql_constraints = [
        ("UniqueEmail", "UNIQUE(email)", "This Email Already Exist")
    ]

    @api.onchange("age")
    def _on_change_pcr(self):
        if not self.age:
            self.age = self.age
            return {}
        if self.age < 30:
            self.pcr = True
        else:
            self.pcr = False
        return {
            'warning': {
                'title': 'Hello',
                'message': 'PCR Is Checked'
            }
        }


class Patient_History(models.Model):
    _name = 'patient_history_line'
    patient_id = fields.Many2one('task.patient')
    description = fields.Text()


class Patient_Customers_Inherit(models.Model):
    _inherit = 'res.partner'

    related_patient_id = fields.Many2one('task.patient')


    def unlink(self):
        for customers in self:
            if customers.related_patient_id:
                raise UserError("Can't Delete This Customer")
        super.unlink()

    _sql_constraints = [
        ("unique", "unique(email)", "email is already exist ")
    ]

    @api.constrains('email')
    def check_email(self):
        for customers in self:
            email_search = customers.env['task.patient'].search([("email", "=", customers.email)])
            if email_search:
                raise UserError("this is email already exist in patient models")
