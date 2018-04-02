import os
import secrets
from os import environ as env

# Flask config
IP = env.get('IP', '0.0.0.0')
PORT = env.get('PORT', 8080)
SERVER_NAME = env.get('SERVER_NAME', 'rides.csh.rit.edu')

# DB Info
SQLALCHEMY_DATABASE_URI = env.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///{}'.format(os.path.join(os.getcwd(), "data.db")))

# Openshift secret
SECRET_KEY = env.get("SECRET_KEY", default=''.join(secrets.token_hex(16)))

# OpenID Connect SSO config
OIDC_ISSUER = env.get('OIDC_ISSUER', 'https://sso.csh.rit.edu/auth/realms/csh')
OIDC_CLIENT_CONFIG = {
    'client_id': env.get('OIDC_CLIENT_ID', 'selections'),
    'client_secret': env.get('OIDC_CLIENT_SECRET', ''),
    'post_logout_redirect_uris': [env.get('OIDC_LOGOUT_REDIRECT_URI', 'https://rides.csh.rit.edu/logout')]
}

LDAP_BIND_DN = env.get("LDAP_BIND_DN", default="cn=rides,ou=Apps,dc=csh,dc=rit,dc=edu")
LDAP_BIND_PASS = env.get("LDAP_BIND_PASS", default=None)

