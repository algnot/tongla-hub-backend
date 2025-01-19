import datetime
import requests
import json
from sqlalchemy import Column, Integer, TIMESTAMP, VARBINARY, TEXT
from model.base import Base
from util.config import get_config


class Email(Base):
    __tablename__ = "email"
    __encrypted_field__ = ["to_email"]

    id = Column(Integer, primary_key=True, autoincrement=True)
    to_email = Column(VARBINARY(200), nullable=False)
    template_id = Column(TEXT, nullable=False)
    send_at = Column(TIMESTAMP, nullable=True)
    status = Column(Integer, nullable=True)
    reason = Column(TEXT, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc),
                                   onupdate=datetime.datetime.now(datetime.timezone.utc))

    def send_email(self, param):
        url = f"{get_config('EMAIL_API_ENDPOINT')}/api/v1.0/email/send"

        payload = json.dumps({
            "service_id": get_config("EMAIL_API_SERVICE_ID"),
            "template_id": self.template_id,
            "user_id": get_config("EMAIL_API_USER_ID"),
            "template_params": param,
            "accessToken": get_config("EMAIL_API_ACCESS_TOKEN")
        })
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        self.update({
            "status": response.status_code,
            "reason": response.text,
            "send_at": datetime.datetime.now(datetime.timezone.utc),
        })

        if response.status_code != 200:
            raise Exception(response.text)

        return self
