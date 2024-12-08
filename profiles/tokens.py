# profiles/tokens.py
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Include email in hash to invalidate token if email changes
        return (
            str(user.pk) + str(timestamp) + 
            str(user.email) + str(user.is_active)
        )

account_activation_token = EmailVerificationTokenGenerator()
