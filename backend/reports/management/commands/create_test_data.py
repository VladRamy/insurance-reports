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
from dateutil.relativedelta import relativedelta

class Command(BaseCommand):
    help = 'Creates complete test data for insurance reports application'

    def handle(self, *args, **options):
        self.stdout.write("Creating comprehensive test data...")
        
        # Очистка старых данных
        self.stdout.write("Cleaning old data...")
        models = [ReserveCalculation, InsuranceClaim, PaymentFlow, Policy, InsuranceProduct, Region]
        for model in models:
            model.objects.all().delete()
        
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

        # 2. Создаем страховые продукты с разными характеристиками
        products = []
        product_types = [
            ('Auto Insurance', 500, 1.2),
            ('Home Insurance', 800, 0.9),
            ('Health Insurance', 1200, 1.5),
            ('Life Insurance', 2000, 0.7),
            ('Travel Insurance', 300, 1.1)
        ]
        
        for i, (name, base_premium, risk_factor) in enumerate(product_types, 1):
            products.append(
                InsuranceProduct.objects.create(
                    name=name,
                    description=f"Comprehensive {name} coverage",
                    base_premium=Decimal(base_premium),
                    risk_factor=risk_factor
                )
            )
        self.stdout.write(f"Created {len(products)} diverse products")

        # 3. Создаем полисы с разными датами (3 года истории)
        policies = []
        for i in range(1, 51):  # 50 полисов
            product = random.choice(products)
            region = random.choice(regions)
            start_date = date.today() - relativedelta(years=random.randint(0, 2), months=random.randint(0, 11))
            
            policy = Policy.objects.create(
                product=product,
                region=region,
                policy_number=f"POL-{start_date.year}-{i:04d}",
                start_date=start_date,
                end_date=start_date + timedelta(days=365),
                premium=product.base_premium * Decimal(str(region.economic_factor)),
                status='active' if start_date + timedelta(days=365) > date.today() else 'expired',
                client_data={
                    'name': f"Client {i}",
                    'email': f"client{i}@example.com",
                    'age': random.randint(18, 70)
                }
            )
            policies.append(policy)
        self.stdout.write(f"Created {len(policies)} policies with 3-year history")

        # 4. Создаем платежи (premium и claim) с историей за 3 года
        payment_flows = []
        today = date.today()
        
        for policy in policies:
            # Премиальные платежи
            for month in range(0, 36):  # 3 года истории
                payment_date = policy.start_date + relativedelta(months=month)
                if payment_date > today:
                    continue
                    
                expected = policy.premium / 12
                actual = expected * Decimal(random.uniform(0.95, 1.05))  # Небольшие колебания
                
                payment_flows.append(
                    PaymentFlow.objects.create(
                        policy=policy,
                        product=policy.product,
                        region=policy.region,
                        payment_type='premium',
                        date=payment_date,
                        expected_amount=expected,
                        actual_amount=actual,
                        is_recurring=True,
                        forecast_accuracy=random.uniform(80, 120)
                    )
                )
            
            # Случайные комиссионные платежи
            if random.random() > 0.7:
                payment_flows.append(
                    PaymentFlow.objects.create(
                        policy=policy,
                        product=policy.product,
                        region=policy.region,
                        payment_type='commission',
                        date=policy.start_date + relativedelta(days=random.randint(30, 180)),
                        expected_amount=policy.premium * Decimal('0.1'),
                        actual_amount=policy.premium * Decimal('0.1') * Decimal(random.uniform(0.9, 1.1)),
                        is_recurring=False
                    )
                )
        
        self.stdout.write(f"Created {len(payment_flows)} payment flows")

        # 5. Создаем страховые случаи с разными статусами и платежами
        claims = []
        for i in range(1, 31):  # 30 страховых случаев
            policy = random.choice(policies)
            event_date = policy.start_date + relativedelta(days=random.randint(30, 300))
            status = random.choices(
                ['open', 'processing', 'paid', 'rejected'],
                weights=[0.2, 0.3, 0.4, 0.1]
            )[0]
            
            estimated = Decimal(str(random.randint(100, 10000)))
            paid = estimated * Decimal(random.uniform(0.7, 1.3)) if status == 'paid' else None
            reserve = estimated * Decimal(random.uniform(0.8, 1.5)) if status in ['open', 'processing'] else Decimal('0')
            
            claim = InsuranceClaim.objects.create(
                policy=policy,
                claim_number=f"CL-{event_date.year}-{i:04d}",
                event_date=event_date,
                report_date=event_date + timedelta(days=random.randint(1, 30)),
                status=status,
                estimated_amount=estimated,
                paid_amount=paid,
                description=f"Claim {i} for {policy.product.name}",
                reserve=reserve,
                is_catastrophic=random.random() > 0.95
            )
            claims.append(claim)
            
            # Платежи по страховым случаям
            if status == 'paid':
                PaymentFlow.objects.create(
                    policy=policy,
                    product=policy.product,
                    region=policy.region,
                    payment_type='claim',
                    date=claim.report_date + timedelta(days=random.randint(1, 30)),
                    expected_amount=claim.estimated_amount,
                    actual_amount=claim.paid_amount,
                    is_recurring=False,
                    forecast_accuracy=random.uniform(70, 130)
                )
        
        self.stdout.write(f"Created {len(claims)} insurance claims with payments")

        # 6. Создаем расчеты резервов с историей (ежеквартально за 2 года)
        for product in products:
            for quarter in range(0, 8):  # 2 года по кварталам
                calc_date = today - relativedelta(months=3*quarter)
                
                total = Decimal(str(random.randint(10000, 100000)))
                required = total * Decimal(random.uniform(0.7, 1.3))
                available = total * Decimal(random.uniform(0.8, 1.5))
                
                ReserveCalculation.objects.create(
                    product=product,
                    calculation_date=calc_date,
                    total_reserves=total,
                    required_reserves=required,
                    available_reserves=available,
                    stress_scenario=random.choice(['low', 'medium', 'high', 'extreme'])
                )
        self.stdout.write(f"Created reserve calculations with 2-year history for all products")

        self.stdout.write(self.style.SUCCESS('Successfully created comprehensive test data!'))