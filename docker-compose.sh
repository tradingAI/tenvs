set -e

cd /root/tenvs & pip install -e . --user

cd /root/tenvs/tenvs
python -m pytest --cov=tenvs