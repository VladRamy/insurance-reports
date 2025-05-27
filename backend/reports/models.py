from django.db import models
from django.db.models import JSONField

class InsuranceProduct(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    base_premium = models.DecimalField(max_digits=12, decimal_places=2)
    risk_factor = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Region(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    economic_factor = models.FloatField(default=1.0)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Policy(models.Model):
    POLICY_STATUS = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('canceled', 'Canceled')
    )
    
    product = models.ForeignKey(InsuranceProduct, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    policy_number = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    premium = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=POLICY_STATUS, default='active')
    client_data = JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.policy_number

class PaymentFlow(models.Model):
    PAYMENT_TYPES = (
        ('premium', 'Premium'),
        ('claim', 'Claim'),
        ('commission', 'Commission')
    )
    
    policy = models.ForeignKey(Policy, on_delete=models.PROTECT, null=True, blank=True)
    product = models.ForeignKey(InsuranceProduct, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, null=True, blank=True)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPES)
    date = models.DateField()
    expected_amount = models.DecimalField(max_digits=12, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_recurring = models.BooleanField(default=False)
    forecast_accuracy = models.FloatField(null=True, blank=True)
    metadata = JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['product']),
            models.Index(fields=['payment_type']),
        ]

    def __str__(self):
        return f"{self.payment_type} - {self.date}"

class InsuranceClaim(models.Model):
    CLAIM_STATUS = (
        ('open', 'Open'),
        ('processing', 'Processing'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected')
    )
    
    policy = models.ForeignKey(Policy, on_delete=models.PROTECT)
    claim_number = models.CharField(max_length=50, unique=True)
    event_date = models.DateField()
    report_date = models.DateField()
    status = models.CharField(max_length=10, choices=CLAIM_STATUS, default='open')
    estimated_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    reserve = models.DecimalField(max_digits=12, decimal_places=2)
    is_catastrophic = models.BooleanField(default=False)
    metadata = JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.claim_number

class ReserveCalculation(models.Model):
    product = models.ForeignKey(InsuranceProduct, on_delete=models.PROTECT)
    calculation_date = models.DateField()
    total_reserves = models.DecimalField(max_digits=12, decimal_places=2)
    required_reserves = models.DecimalField(max_digits=12, decimal_places=2)
    available_reserves = models.DecimalField(max_digits=12, decimal_places=2)
    stress_scenario = models.CharField(max_length=100)
    metadata = JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reserves for {self.product} on {self.calculation_date}"