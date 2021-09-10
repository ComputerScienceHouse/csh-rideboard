from os import environ as env

# Flask config
IP = env.get('IP', '0.0.0.0')
PORT = env.get('PORT', 8080)
SERVER_NAME = env.get('SERVER_NAME', 'rideboard.csh.rit.edu')

# DB Info
SQLALCHEMY_DATABASE_URI = env.get('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = 'False'

# Openshift secret
SECRET_KEY = env.get("SECRET_KEY", default='SECRET-KEY')

# OpenID Connect SSO config CSH
OIDC_ISSUER = env.get('OIDC_ISSUER', 'https://sso.csh.rit.edu/auth/realms/csh')
OIDC_CLIENT_ID = env.get('OIDC_CLIENT_ID', 'rideboard')
OIDC_CLIENT_SECRET = env.get('OIDC_CLIENT_SECRET', 'NOT-A-SECRET')

# Google OpenID Connect SSO config
GOOGLE_ISSUER = env.get('GOOGLE_ISSUER', 'https://accounts.google.com')
GOOGLE_CLIENT_ID = env.get('GOOGLE_CLIENT_ID', '---')
GOOGLE_CLIENT_SECRET = env.get('GOOGLE_CLIENT_SECRET', '---')

LDAP_BIND_DN = env.get("LDAP_BIND_DN", default="cn=rides,ou=Apps,dc=csh,dc=rit,dc=edu")
LDAP_BIND_PASS = env.get("LDAP_BIND_PASS", default=None)

# Slack Config
SLACK_TOKEN = env.get('SLACK_TOKEN','---')

# Mail Config
MAIL_SERVER = env.get("MAIL_SERVER", "thoth.csh.rit.edu")
MAIL_USERNAME = env.get("MAIL_USERNAME", "rideboard@csh.rit.edu")
MAIL_PASSWORD = env.get("MAIL_PASSWORD", None)
MAIL_USE_TLS = True
