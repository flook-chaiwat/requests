# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class RequestRequest(models.Model):
    _inherit = "request.request"

    purchase_request_count = fields.Integer(
        compute="_compute_purchase_request_count"
    )

    @api.depends("product_line_ids.resource_ref")
    def _compute_purchase_request_count(self):
        for request in self:
            lines = request.product_line_ids.filtered(
                lambda l: l.resource_ref
                and l.resource_ref._name == "purchase.request.line"
            )
            purchase_requests = self.env["purchase.request"].browse()
            for line in lines:
                if line.resource_ref:
                    purchase_requests |= line.resource_ref.request_id
            request.purchase_request_count = len(purchase_requests)

    def _prepare_purchase_request(self):
        self.ensure_one()
        val = {
            "origin": self.name,
            "company_id": self.company_id.id,
            "requested_by": self.request_owner_id.id,
            "description": self.reason,
        }
        return val

    def _prepare_purchase_request_line(self, line, purchase_request):
        line_val = {
            "request_id": purchase_request.id,
            "product_id": line.product_id.id,
            "name": line.product_id.display_name,
            "product_qty": line.quantity,
            "product_uom_id": line.product_uom_id.id,
            "estimated_cost": line.price_subtotal,
        }
        return line_val

    def action_create_purchase_request(self):
        self.ensure_one()
        lines = self.product_line_ids._filter_purchase_request_line()
        if not lines:
            return
        val = self.env["purchase.request"].default_get(["name"])
        val.update(self._prepare_purchase_request())
        new = self.env["purchase.request"].create(val)
        for line in lines:
            line_val = self._prepare_purchase_request_line(line, new)
            new_line = self.env["purchase.request.line"].create(line_val)
            line.resource_ref = "{},{}".format(
                new_line._name,
                new_line.id,
            )

    def action_open_purchase_request(self):
        self.ensure_one()
        lines = self.product_line_ids.filtered(
            lambda l: l.resource_ref
            and l.resource_ref._name == "purchase.request.line"
        )
        purchase_requests = self.env["purchase.request"].browse()
        for line in lines:
            if line.resource_ref:
                purchase_requests += line.resource_ref.request_id
        domain = [("id", "in", purchase_requests.ids)]
        action = {
            "name": _("Purchase Request"),
            "view_type": "tree",
            "view_mode": "list,form",
            "res_model": "purchase.request",
            "type": "ir.actions.act_window",
            "context": self.env.context,
            "domain": domain,
        }
        return action
