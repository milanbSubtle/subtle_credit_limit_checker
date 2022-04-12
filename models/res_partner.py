from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class Partner(models.Model):
    _inherit = 'res.partner'

    credit_limit_available = fields.Boolean(string="Credit Limit Available", default=False)
    credit_limit = fields.Monetary(currency_field='res_currency', string="Credit Limit")
    available_credit_limit = fields.Monetary(currency_field='res_currency')
    res_currency = fields.Many2one(comodel_name='res.currency', default=lambda self: self.env.company.currency_id)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        customer_id = self.partner_id.id
        customer_records = self.env['res.partner'].search([('id', '=', customer_id)])

        for customer_record in customer_records:
            if self.amount_total > customer_record.available_credit_limit:
                raise UserError(_("Credit Limit Exceeded."))

        return super(SaleOrder, self).action_confirm()
