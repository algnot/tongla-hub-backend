import datetime
import enum
import uuid
import json
import os
from jwt.utils import get_int_from_datetime
from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, Boolean, Enum, String
from sqlalchemy.orm import relationship
from model.base import Base
from jwt import JWT, jwk_from_pem, jwk_from_dict
from util.encryptor import generate_rsa_keys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
secret_key_path = os.path.join(BASE_DIR, "../secret/secret_key.txt")
rsa_private_key_path = os.path.join(BASE_DIR, "../secret/rsa_private_key.pem")
rsa_public_key_path = os.path.join(BASE_DIR, "../secret/rsa_public_key.json")

class TokenType(enum.Enum):
    ACCESS = 1
    REFRESH = 2
    RESET_PASSWORD = 3

def default_expiration_time():
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=7)

class UserTokens(Base):
    __tablename__ = "user_tokens"

    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="tokens")

    type = Column(Enum(TokenType), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc), nullable=False)
    expires_at = Column(TIMESTAMP, default=default_expiration_time, nullable=False)
    revoked = Column(Boolean, default=False)

    def generate_token(self):
        return self.generate_refresh_token(), self.generate_access_token()

    def generate_jwt(self, expired_in, type: TokenType):
        message = {
            "sub": {
                "user_id": self.user_id,
                "token_id": self.id
            },
            "type": str(type.value),
            "iat": get_int_from_datetime(self.created_at),
            "exp": get_int_from_datetime(datetime.datetime.now(datetime.timezone.utc) + expired_in),
        }

        signing_key = self._load_signing_key()

        jwt_instance = JWT()
        compact_jws = jwt_instance.encode(message, signing_key, alg="RS256")

        return compact_jws

    def verify_token(self, token):
        verifying_key = self._load_verifying_key()
        jwt_instance = JWT()
        payload = jwt_instance.decode(token, verifying_key, do_time_check=True)

        current_time = datetime.datetime.now(datetime.timezone.utc)
        expiration_time = datetime.datetime.fromtimestamp(payload["exp"], datetime.timezone.utc)
        if expiration_time < current_time:
            raise Exception("Token has expired")

        token_data = self.get_by_id(payload["sub"]["token_id"])
        if token_data.revoked:
            raise Exception("Token has revoked")

        return payload


    def _load_signing_key(self):
        try:
            with open(rsa_private_key_path, "rb") as fh:
                return jwk_from_pem(fh.read())
        except FileNotFoundError:
            generate_rsa_keys()
            return self._load_signing_key()

    def _load_verifying_key(self):
        with open(rsa_public_key_path, "r") as fh:
            return jwk_from_dict(json.load(fh))

    def generate_refresh_token(self):
        expired_in = datetime.timedelta(days=14)
        refresh_token = UserTokens()
        refresh_token.create({
            "user_id": self.user_id,
            "expires_at": datetime.datetime.now(datetime.timezone.utc) + expired_in,
            "type": TokenType.REFRESH
        })
        return refresh_token.generate_jwt(expired_in=expired_in, type=TokenType.REFRESH)

    def generate_access_token(self):
        expired_in = datetime.timedelta(days=1)
        access_token = UserTokens()
        access_token.create({
            "user_id": self.user_id,
            "expires_at": datetime.datetime.now(datetime.timezone.utc) + expired_in,
            "type": TokenType.ACCESS
        })
        return access_token.generate_jwt(expired_in, type=TokenType.ACCESS)

    def generate_reset_password_token(self, user_id):
        expired_in = datetime.timedelta(minutes=30)
        access_token = UserTokens()
        access_token.create({
            "user_id": user_id,
            "expires_at": datetime.datetime.now(datetime.timezone.utc) + expired_in,
            "type": TokenType.RESET_PASSWORD
        })
        return access_token.generate_jwt(expired_in, type=TokenType.RESET_PASSWORD)
