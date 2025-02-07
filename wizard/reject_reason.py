# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##########################################################################

from odoo import fields, models


class RejectReason(models.TransientModel):
    _name = "reject.reason"
    _description = 'Reject Reason of Equipment Allocation Request'

    def reject_request(self):
        msg = 'Reject Reason : ' + self.reject_reason
        vals = {'body': msg,
                'author_id': self.env.user and self.env.user.partner_id and self.env.user.partner_id.id,
                'email_from': self.env.user and self.env.user.partner_id and self.env.user.partner_id.email or '',
                'model': 'equipment.allocation',
                'res_id': self.equipment_id.id,
                'message_type': 'comment'}
        self.env['mail.message'].sudo().create(vals)
        self.equipment_id.write({'state': 'rejected', 'reject_reason': self.reject_reason})
        template_id = self.env.ref('dev_equipment_allocation.template_allocation_request_rejected')
        if template_id:
            template_id.send_mail(self.equipment_id.id, force_send=True)

    reject_reason = fields.Text(string='Reject Reason', required=True)
    equipment_id = fields.Many2one('equipment.allocation', string='Equipment Allocation')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: