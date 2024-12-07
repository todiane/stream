# profiles/tokens.py
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import time

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Include email in hash to invalidate token if email changes
        return (
            str(user.pk) + str(timestamp) + 
            str(user.email) + str(user.is_active) +
            str(int(time.time()))  # Add time-based component
        )

account_activation_token = EmailVerificationTokenGenerator()
