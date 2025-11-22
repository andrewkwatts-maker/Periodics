#====== Playtow/PeriodicTable2/run_tests.py ======#
#!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
#!
#!This is the intellectual property of Andrew Keith Watts. Unauthorized
#!reproduction, distribution, or modification of this code, in whole or in part,
#!without the express written permission of Andrew Keith Watts is strictly prohibited.
#!
#!For inquiries, please contact AndrewKWatts@Gmail.com

"""
Test runner with coverage reporting
"""

import unittest
import sys
import os

# Discover and run all tests
loader = unittest.TestLoader()
start_dir = 'tests'
suite = loader.discover(start_dir, pattern='test_*.py')

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Exit with error code if tests failed
sys.exit(0 if result.wasSuccessful() else 1)
