from django.db import models

class BotUser(models.Model):
    user_id = models.BigIntegerField(unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    referral_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.username} ({self.user_id})"

class ReferralCode(models.Model):
    code = models.CharField(max_length=255, unique=True)
    user = models.OneToOneField(BotUser, on_delete=models.CASCADE, related_name='referral_code_rel')

    def __str__(self):
        return self.code

class Participant(models.Model):
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE)
    referral_code = models.ForeignKey(ReferralCode, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Participant: {self.user.username}"

class Referral(models.Model):
    referrer = models.ForeignKey(BotUser, related_name='referrals_made', on_delete=models.CASCADE)
    referred_user = models.ForeignKey(BotUser, related_name='referrals_received', on_delete=models.CASCADE)

    def __str__(self):
        return f"Referral: {self.referrer.username} -> {self.referred_user.username}"