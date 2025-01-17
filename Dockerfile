FROM python:3.10

WORKDIR /mnt
COPY . .

RUN python -m pip install --upgrade pip setuptools
RUN pip install -r requirements.txt

CMD ["python", "-m", "flask", "run"]
