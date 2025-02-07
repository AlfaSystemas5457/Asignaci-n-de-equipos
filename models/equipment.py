# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models, api

class Equipment(models.Model):
    _inherit = 'maintenance.equipment'

    # adding department employees as followers so they can access equipment based on record rule
    def write(self, vals):
        if vals.get('department_id'):
            previous_followers = []
            partner_ids = []
            previous_follower_ids = self.env['mail.followers'].sudo().search([('res_model', '=', 'maintenance.equipment'),
                                                                              ('res_id', '=', self.id)])
            for p_f in previous_follower_ids:
                if p_f.partner_id:
                    previous_followers.append(p_f.partner_id.id)
            employee_ids = self.env['hr.employee'].search([('user_id', '!=', False),
                                                           ('department_id', '=', vals['department_id'])])
            for employee_id in employee_ids:
                if employee_id.user_id and employee_id.user_id.partner_id:
                    if employee_id.user_id.partner_id.id not in previous_followers:
                        partner_ids.append(employee_id.user_id.partner_id.id)
            if partner_ids:
                self.message_subscribe(partner_ids=partner_ids)
        return super(Equipment, self).write(vals)

    # adding department employees as followers so they can access equipment based on record rule
    def create(self, vals):
        equipment_id = super(Equipment, self).create(vals)
        if equipment_id.department_id:
            previous_followers = []
            partner_ids = []
            previous_follower_ids = self.env['mail.followers'].sudo().search([('res_model', '=', 'maintenance.equipment'),
                                                                              ('res_id', '=', equipment_id.id)])
            for p_f in previous_follower_ids:
                if p_f.partner_id:
                    previous_followers.append(p_f.partner_id.id)
            employee_ids = self.env['hr.employee'].search([('user_id', '!=', False),
                                                           ('department_id', '=', equipment_id.department_id.id)])
            for employee_id in employee_ids:
                if employee_id.user_id and employee_id.user_id.partner_id:
                    if employee_id.user_id.partner_id.id not in previous_followers:
                        partner_ids.append(employee_id.user_id.partner_id.id)
            if partner_ids:
                equipment_id.message_subscribe(partner_ids=partner_ids)
        return equipment_id

    def _compute_allocation_count(self):
        for rec in self:
            allocation_ids = self.env['equipment.allocation'].search([('equipment_id', '=', rec.id)])
            print("allocation_ids==============",allocation_ids)
            rec.allocation_count = len(allocation_ids)

    def view_allocation(self):
        allocation_ids = self.env['equipment.allocation'].search([('equipment_id', '=', self.id)])
        action = self.env.ref('dev_equipment_allocation.action_equipment_allocation_dev_equipment_allocation').read()[0]
        if len(allocation_ids) > 1:
            action['domain'] = [('id', 'in', allocation_ids.ids)]
        elif len(allocation_ids) == 1:
            action['views'] = [(self.env.ref('dev_equipment_allocation.form_equipment_allocation_dev_equipment_allocation').id, 'form')]
            action['res_id'] = allocation_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    state = fields.Selection(string='Status', selection=[('available', 'Available'),
                                                         ('allocated', 'Allocated')],
                             default='available', tracking=1)
    allocation_count = fields.Integer(string='Allocation Count', compute='_compute_allocation_count')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: