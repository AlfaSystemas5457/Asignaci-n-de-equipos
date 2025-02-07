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


class ReplaceEquipment(models.TransientModel):
    _name = "replace.equipment"
    _description = 'Replace Equipment'

    def replace_equipment(self):
        action = self.env.ref('dev_equipment_allocation.action_equipment_replacement_dev_equipment_allocation').sudo().read()[0]
        context = action['context']
        if 'is_replace_request' in context:
            context.pop('is_replace_request')
        new_equipment_id = self.allocation_id.with_context({'context': context}).copy({'equipment_id': self.equipment_id.id,
                                                                                       'is_replace_request': True,
                                                                                       'replaced_allocation_id': self.allocation_id.id})
        action.update({'res_id': new_equipment_id.id, 'domain': [('id', '=', new_equipment_id.id)]})
        return action

    allocation_id = fields.Many2one('equipment.allocation', string='Equipment Allocation')
    equipment_id = fields.Many2one('maintenance.equipment',
                                   string='Equipment',
                                   required=True,
                                   domain=[('state', '!=', 'allocated')])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: