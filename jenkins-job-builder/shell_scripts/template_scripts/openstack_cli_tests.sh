set +e

SSH_OPTIONS='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'

# Get openstack CLI version
OPENSTACK_VER=$(ssh -i $FUEL_KEY $SSH_OPTIONS root@$CONTROLLER_IP \
    'openstack --version 2>&1 | awk "{ print \$2 }"')

# Create vitrualenv
virtualenv --clear venv
. venv/bin/activate

pip install tox

# Clone source
git clone -b $OPENSTACK_VER https://github.com/openstack/python-openstackclient

cd python-openstackclient

# install subunit2junitxml with dependencies
pip install -U python_subunit junitxml

# WA wrong version of openstack client installed as dependency of ironic client
echo "python-openstackclient==$OPENSTACK_VER" >> test-requirements.txt

# Run tests
tox \
    -e functional -- \
    -r '^(?!functional\.tests\.identity\.v3)' \
    --no-pretty \
    -s \
| subunit2junitxml \
    --forward \
    --output-to=../$REPORT_FILE \
| subunit2pyunit

deactivate

dos.py destroy "$ENV_NAME"
