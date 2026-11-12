# Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and Contributors
# See license.txt

# import frappe
from frappe.tests import IntegrationTestCase


# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]



class IntegrationTestShadeMatchRequest(IntegrationTestCase):
	"""
	Integration tests for ShadeMatchRequest.
	Use this class for testing interactions between multiple components.
	"""

	pass
