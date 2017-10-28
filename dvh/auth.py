#!/usr/bin/env python

# Users that wish to implement some form of user authentication should fill in this function, keeping the same input
# parameters.  The following example is for LDAP.  Note that proper implementation also necessitates running your
# Bokeh with a reverse proxy implementing SSL with something like Apache or NGINX.  Please see Bokeh documentation for
# some guidance on this. I (the DVH Analytics developer) do not claim to be a security expert by any stretch.  The
# end-user is entirely liable for proper security implementation.

from __future__ import print_function
from bokeh.models.widgets import Button, TextInput, PasswordInput
from bokeh.layouts import row
from bokeh.models import Spacer
# import ldap  # This is from pip install python-ldap.  Not necessary, just what we used for our implementaiton.


# Place holder function.  Edit this to implement.
def check_credentials(username, password, usergroup):

    # ############################
    # # Example Code
    # ############################
    # """Verifies credentials for username and password.
    # Returns None on success or a string describing the error on failure
    # # Adapt to your needs
    # """
    # LDAP_SERVER = 'ldaps://someserver:port'
    # # fully qualified AD user name
    # LDAP_USERNAME = '%s@somedomain' % username
    # # your password
    # LDAP_PASSWORD = password
    # base_dn = 'somebasedn'
    # ldap_filter = 'userPrincipalName=%s@somedomain' % username
    # try:
    #     # build a client
    #     ldap_client = ldap.initialize(LDAP_SERVER)
    #
    #     # perform a synchronous bind
    #     ldap_client.set_option(ldap.OPT_REFERRALS, 0)
    #     ldap_client.simple_bind_s(LDAP_USERNAME, LDAP_PASSWORD)
    #
    #     # get all user attributes
    #     result = ldap_client.search_s(base_dn, ldap.SCOPE_SUBTREE, ldap_filter)
    #     ldap_client.unbind()
    # except ldap.INVALID_CREDENTIALS:
    #     ldap_client.unbind()
    #     print("Login attempt: Invalid credentials")
    #     return False
    # except ldap.SERVER_DOWN:
    #     print("Login attempt: Server down")
    #     return False
    # except ldap.LDAPError, e:
    #     ldap_client.unbind()
    #     if type(e.message) == dict and 'desc' in e.message:
    #         print("Login error: %s" % e.message['desc'])
    #         return False
    #     else:
    #         print("Login error: %s" % e.message)
    #         return False
    #     ldap_client.unbind()

    return True
