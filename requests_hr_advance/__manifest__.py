# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Requests -> Employee Advance",
    "version": "14.0.1.0.0",
    "category": "Human Resources/Requests",
    "website": "https://github.com/OCA/account-payment",
    "summary": """
        This module adds to the requests workflow the possibility to generate
        Employee Advance from an Requests.
    """,
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["requests", "hr_expense_advance_clearing"],
    "data": [
        "data/ir_actions_server.xml",
        "data/request_category_data.xml",
        "views/request_views.xml",
    ],
    "demo": [
        "data/request_demo.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": True,
}