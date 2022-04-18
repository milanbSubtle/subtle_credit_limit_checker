from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class Partner(models.Model):
    _inherit = 'res.partner'

    credit_limit_available = fields.Boolean(string="Credit Limit Available", default=False)
    credit_limit = fields.Monetary(currency_field='res_currency', string="Credit Limit")
    available_credit_limit = fields.Monetary(currency_field='res_currency', string="Available Credit Limit",
                                             compute='compute_available_credit_limit')
    total_pending_payments = fields.Monetary(currency_field='res_currency', string="Total Pending Payments",
                                             compute='compute_total_pending')
    res_currency = fields.Many2one(comodel_name='res.currency', default=lambda self: self.env.company.currency_id)

    def compute_total_pending(self):
        self.total_pending_payments = self.total_due

    def compute_available_credit_limit(self):
        self.available_credit_limit = self.credit_limit - self.total_due


class SaleOrder(models.Model):
    _inherit = "sale.order"

# confirm quotation if amount_total > available_credit_limit
    def action_confirm(self):
        customer_id = self.partner_id.id
        customer_records = self.env['res.partner'].search([('id', '=', customer_id)])

        for customer_record in customer_records:
            if customer_record.credit_limit_available:
                if self.amount_total > customer_record.available_credit_limit:
                    raise UserError(_("Credit Limit Exceeded."))

        return super(SaleOrder, self).action_confirm()


class AccountMove(models.Model):
    _inherit = "account.move"

# confirm invoice
    def action_post(self):

        customer_id = self.partner_id.id
        customer_records = self.env['res.partner'].search([('id', '=', customer_id)])

        # calculate available_credit_limit and total due
        for customer_record in customer_records:
            for record in customer_record:
                total_due = 0
                for aml in record.unreconciled_aml_ids:
                    if aml.company_id == self.env.company and not aml.blocked:
                        amount = aml.amount_residual
                        total_due += amount

            customer_record.available_credit_limit = customer_record.credit_limit - total_due
            if customer_record.available_credit_limit:
                customer_record.available_credit_limit = 0

            customer_record.total_pending_payments = total_due

        return super(AccountMove, self).action_post()

# Register payment
    def action_register_payment(self):

        customer_id = self.partner_id.id
        customer_records = self.env['res.partner'].search([('id', '=', customer_id)])

        # calculate available_credit_limit and total due after payment
        for customer_record in customer_records:
            invoice_payment = self.amount_total - self.amount_residual
            customer_record.total_pending_payments -= invoice_payment
            customer_record.available_credit_limit += invoice_payment
        
        return super(AccountMove, self).action_register_payment()
