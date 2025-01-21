# profiles/tokens.py
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import logging

logger = logging.getLogger(__name__)

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        """
        Hash using values that will remain constant until email is verified
        """
        # Log the values being used in hash generation
        logger.debug(f"[Token Generation] User ID: {user.pk}")
        logger.debug(f"[Token Generation] Timestamp: {timestamp}")
        logger.debug(f"[Token Generation] Email: {user.email}")
        logger.debug(f"[Token Generation] Profile verified status: {user.profile.email_verified}")
        
        # Create hash using profile.email_verified instead of user.is_active
        hash_string = (
            f"{user.pk}{timestamp}"
            f"{user.email}"
            f"{user.profile.email_verified}"
        )
        
        logger.debug(f"[Token Generation] Final hash string: {hash_string}")
        return hash_string

    def check_token(self, user, token):
        """
        Override check_token to add logging
        """
        logger.debug(f"[Token Verification] Checking token for user: {user.username}")
        logger.debug(f"[Token Verification] Provided token: {token}")
        
        result = super().check_token(user, token)
        logger.debug(f"[Token Verification] Token valid: {result}")
        return result

account_activation_token = EmailVerificationTokenGenerator()