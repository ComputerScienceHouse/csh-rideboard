import secrets
from os import environ as env

# Flask config
IP = env.get('IP', '0.0.0.0')
PORT = env.get('PORT', 8080)
SERVER_NAME = env.get('SERVER_NAME', 'rideboard.csh.rit.edu')

# DB Info
SQLALCHEMY_DATABASE_URI = env.get('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = 'False'

# Openshift secret
SECRET_KEY = env.get("SECRET_KEY", default='61f48bcb-a530')

# OpenID Connect SSO config
OIDC_ISSUER = env.get('OIDC_ISSUER', 'https://sso.csh.rit.edu/auth/realms/csh')
OIDC_CLIENT_CONFIG = {
    'client_id': env.get('OIDC_CLIENT_ID', 'rideboard'),
    'client_secret': env.get('OIDC_CLIENT_SECRET', ''),
    'post_logout_redirect_uris': [env.get('OIDC_LOGOUT_REDIRECT_URI', 'https://rideboard.csh.rit.edu/logout')]
}

LDAP_BIND_DN = env.get("LDAP_BIND_DN", default="cn=rides,ou=Apps,dc=csh,dc=rit,dc=edu")
LDAP_BIND_PASS = env.get("LDAP_BIND_PASS", default=None)
