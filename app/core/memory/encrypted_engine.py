import os
import json
from cryptography.fernet import Fernet

class EncryptedMemoryEngine:
    """
    Wraps any memory engine to encrypt values before saving,
    and decrypt them on fetch. Usernames and keys are not encrypted.
    """

    def __init__(self, underlying_engine):
        """
        Create an encrypted memory engine wrapper.

        Args:
            underlying_engine: Any engine with save/fetch/clear methods
        """
        self.engine = underlying_engine
        key = os.environ.get("FERNET_KEY")
        if not key:
            # Strongly recommended: set FERNET_KEY in prod (never commit to source!)
            key = Fernet.generate_key()
            print(f"WARNING: FERNET_KEY not set! Using transient key: {key.decode()}")
        self.cipher = Fernet(key)
        try:
            Fernet(os.environ["FERNET_KEY"])
        except Exception as e:
            raise RuntimeError("❌ Invalid FERNET_KEY in env. Must be 32-byte Base64!") from e

    def save(self, user, key, value):
        """
        Encrypt and store value for the user+key.

        Args:
            user (str): Username
            key (str): Memory key
            value (str|json): Data to store (auto-serialized)
        """
        plaintext = value.encode() if isinstance(value, str) else json.dumps(value).encode()
        ciphertext = self.cipher.encrypt(plaintext)
        self.engine.save(user, key, ciphertext.decode())

    def fetch(self, user, key):
        """
        Fetch value, decrypting it before returning.

        Args:
            user (str): Username/session
            key (str): Memory key

        Returns:
            Original decoded value, or None
        """
        ciphertext = self.engine.fetch(user, key)
        if ciphertext:
            try:
                plaintext = self.cipher.decrypt(ciphertext.encode())
                try:
                    return json.loads(plaintext)
                except Exception:
                    return plaintext.decode()
            except Exception:
                return None
        return None

    def clear(self, user):
        """
        Clear all memory for a user.
        """
        self.engine.clear(user)