set -e

cd /root/tenvs && pip install -e .

cd /root/tenvs/tenvs && python -m pytest --cov=tenvs