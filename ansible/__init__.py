import os
# Extend package path to include the actual ansible implementation under lib/ansible
package_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib', 'ansible'))
if os.path.isdir(package_dir):
    __path__.append(package_dir)
