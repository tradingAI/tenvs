set -e

pip install pytest

cd /root/tenvs & pip install -e . --user

cd /root/tenvs/tenvs
python -m pytest --cov=tenvs