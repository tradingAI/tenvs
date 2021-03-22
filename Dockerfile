FROM aiminders/python:3.8.7

# install tenvs
WORKDIR  $CODE_DIR
RUN cd $CODE_DIR && rm -rf tenvs
RUN git clone https://github.com/tradingAI/tenvs.git
# Clean up pycache and pyc files
RUN cd $CODE_DIR/tenvs && rm -rf __pycache__ && \
    find . -name "*.pyc" -delete && \
    pip install -e .

RUN rm -rf /root/.cache/pip \
    && find / -type d -name __pycache__ -exec rm -r {} \+

WORKDIR $CODE_DIR/tenvs

CMD /bin/bash
