# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models, api, _, _lt
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError

class EquipmentAllocation(models.Model):
    _name = 'equipment.allocation'
    _description = 'Equipment Allocation'
    _inherit = ['mail.thread']

    def equipment_allocation_reminder(self):
        before_days = self.env.company and self.env.company.er_before_days
        if before_days > 0:
            expiry_date = date.today() + timedelta(days=int(before_days))
            allocation_ids = self.env['equipment.allocation'].search([('state', '=', 'allocated'),
                                                                      ('return_date',  '=', expiry_date)])
            template_id = self.env.ref('dev_equipment_allocation.template_allocation_return_reminder')
            if allocation_ids:
                for allocation_id in allocation_ids:
                    template_id.send_mail(allocation_id.id, force_send=True)

    def unlink(self):
        # if any('draft' != rec.state for rec in self):
        #     raise ValidationError(_('''Only 'New' request can be deleted'''))
        return super(EquipmentAllocation, self).unlink()

    def get_return_date(self):
        return_date = ''
        if self.return_date:
            return_date = datetime.strptime(str(self.return_date), "%Y-%m-%d").strftime('%d-%m-%Y')
        return return_date

    @api.returns('self')
    def _get_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1) or False
    
    def create_report(self):
        return self.env.ref('dev_equipment_allocation.report_template_id').report_action(self)
        
        # # raise ValidationError(data['day'])
        # return self.env.ref('dev_equipment_allocation.report_equipment_allocation_action').report_action(self, data={'data':data})
        
        

    def submit_to_manager(self):
        allocation_id = self.env['equipment.allocation'].search([('equipment_id', '=', self.equipment_id.id),
                                                                  ('id', '!=', self.id),
                                                                  ('state', 'in', ['submitted','allocated'])], limit=1)
        if allocation_id:
            raise ValidationError(_('''Request %s is already pending for %s equipment which is requested by %s, you can not make new request''') %
                                  (allocation_id.number, allocation_id.equipment_id.name, allocation_id.employee_id.name))
        self.state = 'allocated'
        template_id = self.env.ref('dev_equipment_allocation.template_allocation_request_submitted')
        if template_id:
            group_id = self.env.ref('maintenance.group_equipment_manager')
            if group_id and group_id.users:
                partners = []
                for u_id in group_id.users:
                    if u_id.partner_id:
                        partners.append(u_id.partner_id.id)
                if partners:
                    template_id.partner_to = ', '.join(map(str, partners))
            template_id.send_mail(self.id, force_send=True)
            template_id.partner_to = ''

    def allocate_equipment(self):
        self.allocation_date = date.today()
        if self.allocation_type == 'on_demand':
            if self.duration_type == 'year':
                self.return_date = date.today() + relativedelta(years=+self.duration) - relativedelta(days=1)
            elif self.duration_type == 'month':
                self.return_date = date.today() + relativedelta(months=+self.duration) - relativedelta(days=1)
            elif self.duration_type == 'week':
                self.return_date = date.today() + relativedelta(weeks=+self.duration) - relativedelta(days=1)
            elif self.duration_type == 'day':
                self.return_date = date.today() + relativedelta(days=+self.duration) - relativedelta(days=1)
        self.state = 'allocated'
        self.equipment_id.state = 'allocated'
        self.equipment_id.employee_id = self.employee_id.id
        if self.is_replace_request:
            self.replaced_allocation_id.return_equipment()
        template_id = self.env.ref('dev_equipment_allocation.template_allocation_request_allocated')
        if template_id:
            template_id.send_mail(self.id, force_send=True)

    def reject_request(self):
        action = self.env.ref('dev_equipment_allocation.action_popup_reject_reason_dev_equipment_allocation').sudo().read()[0]
        return action

    def set_to_draft(self):
        self.state = 'draft'

    def return_equipment(self):
        self.state = 'returned'
        self.actual_return_date = date.today()
        self.equipment_id.state = 'available'
        self.equipment_id.employee_id = False

    def replace_equipment(self):
        replacement_id = self.env['equipment.allocation'].search([('replaced_allocation_id', '=', self.id),
                                                                  ('state', 'in', ['submitted', 'draft'])], limit=1)

        if replacement_id:
            raise ValidationError(
                _('''Request %s is already pending for %s equipment which is requested by %s, you can not make new request''') %
                (replacement_id.number, replacement_id.equipment_id.name, replacement_id.employee_id.name))
        action = self.env.ref('dev_equipment_allocation.action_replace_equipment_dev_equipment_allocation').sudo().read()[0]
        return action

    def view_replaced_allocation(self):
        allocation_ids = self.env['equipment.allocation'].search([('replaced_allocation_id', '=', self.id),
                                                                  ('is_replace_request', '=', True)])
        action = self.env.ref('dev_equipment_allocation.action_equipment_allocation_dev_equipment_allocation').sudo().read()[0]
        if len(allocation_ids) > 1:
            action['domain'] = [('id', 'in', allocation_ids.ids)]
        elif len(allocation_ids) == 1:
            action['views'] = [(self.env.ref('dev_equipment_allocation.form_equipment_allocation_dev_equipment_allocation').id, 'form')]
            action['res_id'] = allocation_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def view_allocation_request(self):
        action = self.env.ref('dev_equipment_allocation.action_equipment_allocation_dev_equipment_allocation').sudo().read()[0]
        action['views'] = [(self.env.ref('dev_equipment_allocation.form_equipment_allocation_dev_equipment_allocation').id, 'form')]
        action['res_id'] = self.replaced_allocation_id.id
        return action

    def restrict_allocation(self):
        raise ValidationError(_('''Equipment Replacement Request is automatically created when you replace Allocated Equipment, Do not create it manually.'''))

    @api.model_create_multi
    def create(self, vals):
        record = super(EquipmentAllocation, self).create(vals)
        
        if 'replacement' in self._context:
            self.restrict_allocation()
        if 'is_replace_request' in vals:
            sequence_number = self.env['ir.sequence'].next_by_code('sequence.equipment.mode.one') or '/'
            record.number = f"MIR-{record.area}-{record.doc_type}-RE-{sequence_number}"
        else:
            sequence_number = self.env['ir.sequence'].next_by_code('sequence.equipment.mode.one') or '/'
            record.number = f"MIR-{record.area}-{record.doc_type}-AE-{sequence_number}"
        
        return record

    def _compute_has_replacement(self):
        for rec in self:
            flag = False
            replacement_ids = rec.env['equipment.allocation'].search([('replaced_allocation_id', '=', rec.id),
                                                                      ('is_replace_request', '=', True)])
            if replacement_ids:
                flag = True
            rec.has_replacement = flag

    def allocation_url(self):
        ir_param = self.env['ir.config_parameter'].sudo()
        base_url = ir_param.get_param('web.base.url')
        action_id = self.env.ref('dev_equipment_allocation.action_equipment_allocation_dev_equipment_allocation').id
        menu_id = self.env.ref('maintenance.menu_maintenance_title').id
        if base_url:
            base_url += '/web#id=%s&action=%s&model=%s&view_type=form&cids=&menu_id=%s' % (int(self.id), action_id, self._name, menu_id)
        return base_url

    def _compute_over_due_days(self):
        for rec in self:
            od_date = 0
            if rec.return_date and date.today() > rec.return_date:
                od_date = (date.today() - rec.return_date).days
            rec.over_due_days = od_date
            
    name = fields.Char(string='Name', tracking=1, required=True)
    number = fields.Char(string='Number', tracking=1)
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=1, required=True, default=_get_employee)
    equipment_id = fields.Many2one('maintenance.equipment',
                                   string='Equipment',
                                   tracking=1, required=True,
                                   domain=[('state', '!=', 'allocated')])
    request_date = fields.Date(string='Request Date', required=True, default=date.today())
    allocation_type = fields.Selection(string='Allocation Type', selection=[('on_demand', 'Bajo demanda'),
                                                                            ('permanent', 'Permanente')],
    # allocation_type = fields.Selection(string='Allocation Type', selection=[('on_demand', 'On Demand'),
    #                                                                         ('permanent', 'Permanent')],
                                       default='on_demand', tracking=1, required=True)
    duration = fields.Integer("Duration", tracking=1, default=1, required=True)
    duration_type = fields.Selection(selection=[('day', 'Dias'),
                                                ('week', 'Semanas'),
                                                ('month', 'Meses'),
                                                ('year', 'Años')], default="month",
    # duration_type = fields.Selection(selection=[('day', 'Days'),
    #                                             ('week', 'Weeks'),
    #                                             ('month', 'Months'),
    #                                             ('year', 'Years')], default="month",
                                     tracking=1, required=True)
    allocation_date = fields.Date(string="Allocation Date", tracking=1, copy=False)
    return_date = fields.Date(string="Expected Return Date", tracking=1, copy=False)
    actual_return_date = fields.Date(string='Return Date', copy=False, tracking=1)
    state = fields.Selection(string='Status', selection=[('draft', 'Nuevo'),
                                                        #  ('submitted', 'Waiting for Approval'),
                                                         ('allocated', 'Asignado'),
                                                         ('rejected', 'Rechazado'),
                                                         ('returned', 'Devuelto')],
    # state = fields.Selection(string='Status', selection=[('draft', 'New'),
    #                                                     #  ('submitted', 'Waiting for Approval'),
    #                                                      ('allocated', 'Allocated'),
    #                                                      ('rejected', 'Rejected'),
    #                                                      ('returned', 'Returned')],
                             default='draft', tracking=1, required=True)
    reject_reason = fields.Text(string='Reject Reason', copy=False)
    replaced_allocation_id = fields.Many2one('equipment.allocation',
                                             string='Replaced Allocation',
                                             copy=False)
    is_replace_request = fields.Boolean(string='Is Replace?', copy=False)
    has_replacement = fields.Boolean(string='Has Replacement', compute='_compute_has_replacement')
    over_due_days = fields.Integer(string='Overdue Days', compute='_compute_over_due_days')
    description = fields.Text(string='Description')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
