from django.core.management.base import BaseCommand
from reports.models import (
    InsuranceProduct,
    Region,
    Policy,
    PaymentFlow,
    InsuranceClaim,
    ReserveCalculation
)
from decimal import Decimal
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Creates complete test data for insurance reports application'

    def handle(self, *args, **options):
        self.stdout.write("Creating test data...")
        
        # 1. Создаем регионы
        regions = [
            Region.objects.create(
                name=f"Region {i}",
                code=f"REG{i:03d}",
                economic_factor=round(random.uniform(0.8, 1.2), 2)
            )
            for i in range(1, 6)
        ]
        self.stdout.write(f"Created {len(regions)} regions")

        # 2. Создаем страховые продукты
        products = [
            InsuranceProduct.objects.create(
                name=f"Product {i}",
                description=f"Description for product {i}",
                base_premium=Decimal(str(random.randint(100, 1000))),
                risk_factor=round(random.uniform(0.5, 2.0), 2)
            )
            for i in range(1, 6)
        ]
        self.stdout.write(f"Created {len(products)} products")

        # 3. Создаем полисы
        policies = []
        for i in range(1, 21):
            product = random.choice(products)
            region = random.choice(regions)
            start_date = date(2023, 1, 1) + timedelta(days=random.randint(0, 365))
            
            policies.append(
                Policy.objects.create(
                    product=product,
                    region=region,
                    policy_number=f"POL-2023-{i:04d}",
                    start_date=start_date,
                    end_date=start_date + timedelta(days=365),
                    premium=product.base_premium * Decimal(str(region.economic_factor)),
                    status=random.choice(['active', 'active', 'active', 'expired', 'canceled']),
                    client_data={
                        'name': f"Client {i}",
                        'email': f"client{i}@example.com"
                    }
                )
            )
        self.stdout.write(f"Created {len(policies)} policies")

        # 4. Создаем платежи
        payment_flows = []
        for policy in policies:
            for month in range(1, 13):
                payment_date = policy.start_date + timedelta(days=30*month)
                if payment_date > date.today():
                    continue
                    
                payment_flows.append(
                    PaymentFlow.objects.create(
                        policy=policy,
                        product=policy.product,
                        region=policy.region,
                        payment_type='premium',
                        date=payment_date,
                        expected_amount=policy.premium / 12,
                        actual_amount=policy.premium / 12,
                        is_recurring=True
                    )
                )
        self.stdout.write(f"Created {len(payment_flows)} premium payments")

        # 5. Создаем страховые случаи
        claims = []
        for i, policy in enumerate(random.sample(policies, 5)):  # 5 случайных полисов с claims
            event_date = policy.start_date + timedelta(days=random.randint(30, 300))
            
            claims.append(
                InsuranceClaim.objects.create(
                    policy=policy,
                    claim_number=f"CL-2023-{i:04d}",
                    event_date=event_date,
                    report_date=event_date + timedelta(days=random.randint(1, 30)),
                    status=random.choice(['open', 'processing', 'paid', 'paid', 'rejected']),
                    estimated_amount=Decimal(str(random.randint(100, 5000))),
                    paid_amount=Decimal(str(random.randint(100, 5000))) if random.random() > 0.3 else None,
                    description=f"Claim description {i}",
                    reserve=Decimal(str(random.randint(500, 10000))),
                    is_catastrophic=random.random() > 0.9
                )
            )
            
            # Добавляем payment flow для claim
            PaymentFlow.objects.create(
                policy=policy,
                product=policy.product,
                region=policy.region,
                payment_type='claim',
                date=claims[-1].report_date,
                expected_amount=claims[-1].estimated_amount,
                actual_amount=claims[-1].paid_amount,
                is_recurring=False
            )
        self.stdout.write(f"Created {len(claims)} insurance claims")

        # 6. Создаем расчеты резервов
        for product in products:
            ReserveCalculation.objects.create(
                product=product,
                calculation_date=date.today(),
                total_reserves=Decimal(str(random.randint(10000, 100000))),
                required_reserves=Decimal(str(random.randint(8000, 90000))),
                available_reserves=Decimal(str(random.randint(10000, 100000))),
                stress_scenario=random.choice(['low', 'medium', 'high'])
            )
        self.stdout.write(f"Created reserve calculations for all products")

        self.stdout.write(self.style.SUCCESS('Successfully created all test data!'))