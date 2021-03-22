set -e

pip install pytest pytest-cov

cd /root/tenvs & pip install -e .

cd /root/tenvs/tenvs
python -m pytest --cov=tenvs