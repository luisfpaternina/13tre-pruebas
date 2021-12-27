from odoo import _, api, fields, models


class HrEmployeeInternalRequestTrasient(models.TransientModel):
    _name = 'hr.employee.internal.request.wizard'

    reason_for_rejection = fields.Text(
        'Reason for rejection',
        size=200)

    reason_for_cancellation = fields.Text(
        'Reason for cancellation',
        size=200)

    approval_reason = fields.Text(
        'Approval_reason',
        size=200)

    def return_internal_request(self):
        context = self.env.context

        ir_current = self.env['hr.employee.internal.request']\
            .browse(context.get('active_id'))
        stage = self.env['hr.employee.internal.request.stages']\
            .browse(context.get('ir_stage_id'))

        ir_current.write(dict(
            reason_for_rejection=self.reason_for_rejection,
            stage_id=stage
        ))

        return {'type': 'ir.actions.act_window_close'}

    def cancel_internal_request(self):
        context = self.env.context

        ir_current = self.env['hr.employee.internal.request']\
            .browse(context.get('active_id'))
        stage = self.env['hr.employee.internal.request.stages']\
            .browse(context.get('ir_stage_id'))

        ir_current.write(dict(
            reason_for_cancellation=self.reason_for_cancellation,
            stage_id=stage
        ))

        return {'type': 'ir.actions.act_window_close'}

    def approval_internal_request(self):
        context = self.env.context

        ir_current = self.env['hr.employee.internal.request']\
            .browse(context.get('active_id'))
        stage = self.env['hr.employee.internal.request.stages']\
            .browse(context.get('ir_stage_id'))

        ir_current.write(dict(
            approval_reason=self.approval_reason,
            stage_id=stage
        ))

        return {'type': 'ir.actions.act_window_close'}
