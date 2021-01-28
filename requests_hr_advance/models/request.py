# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class RequestRequest(models.Model):
    _inherit = "request.request"

    hr_advance_count = fields.Integer(compute="_compute_hr_advance_count")

    @api.depends("resource_ref")
    def _compute_hr_advance_count(self):
        for request in self:
            ref = request.resource_ref
            request.hr_advance_count = (
                1
                if (ref and ref._name == "hr.expense.sheet" and ref.advance)
                else 0
            )

    def action_create_hr_advance(self):
        self.ensure_one()
        if not self.amount > 0:  # No amount, no create advance
            return
        values = {
            "advance": True,
            "unit_amount": self.amount,
        }
        Expense = self.env["hr.expense"]
        specs = Expense._onchange_spec()
        updates = Expense.onchange(values, ["advance"], specs)
        value = updates.get("value", {})
        for name, val in value.items():
            if isinstance(val, tuple):
                value[name] = val[0]
        values.update(value)
        advance = Expense.create(values)
        advance.action_submit_expenses()
        self.resource_ref = "{},{}".format(
            advance.sheet_id._name,
            advance.sheet_id.id,
        )

    def action_open_hr_advance(self):
        self.ensure_one()
        sheet = (
            self.resource_ref
            if (
                self.resource_ref
                and self.resource_ref._name == "hr.expense.sheet"
                and self.resource_ref.advance
            )
            else self.env["hr.expense.sheet"].browse()
        )
        domain = [("id", "=", sheet.id)]
        action = {
            "name": _("Advance"),
            "view_type": "tree",
            "view_mode": "list,form",
            "res_model": "hr.expense.sheet",
            "type": "ir.actions.act_window",
            "context": self.env.context,
            "domain": domain,
        }
        return action
