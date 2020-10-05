FROM python:3.8

CMD cp -r /python /asset-output

COPY requirements.txt /
RUN pip install -t /python -r /requirements.txt \
	&& rm -rf /python/**/__pycache__
