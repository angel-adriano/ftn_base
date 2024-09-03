{
    "name": "Login As Another User (Impersonate)",
    "summary": """Login as another user. Impersonate another user.""",
    "description": """
        Login as another user. Impersonate another user.
    """,
    "author": "Sanesquare Technologies",
    "website": "https://www.sanesquare.com/",
    "support": "odoo@sanesquare.com",
    "license": "OPL-1",
    "category": "Uncategorized",
    "version": "14.0.1.0.1",
    "images": ["static/description/ssq_login_as_user_v14.png"],
    "depends": ["base"],
    "data": [
        "security/security.xml",
        "views/res_users_view.xml",
    ],
}
