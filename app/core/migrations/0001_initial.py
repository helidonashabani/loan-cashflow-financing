# Generated by Django 3.2.9 on 2021-11-20 22:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=100, unique=True)),
                ('issue_date', models.DateField()),
                ('total_amount', models.FloatField()),
                ('rating', models.PositiveIntegerField()),
                ('maturity_date', models.DateField()),
                ('total_expected_interest_amount', models.FloatField()),
                ('invested_amount', models.FloatField(null=True)),
                ('investment_date', models.DateField(null=True)),
                ('expected_interest_amount', models.FloatField(null=True)),
                ('is_closed', models.BooleanField(default=False, null=True)),
                ('expected_irr', models.FloatField(null=True)),
                ('realized_irr', models.FloatField(null=True)),
            ],
            options={
                'verbose_name': 'Loan',
            },
        ),
        migrations.CreateModel(
            name='CashFlow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference_date', models.DateField()),
                ('type', models.CharField(max_length=50)),
                ('amount', models.FloatField()),
                ('loan_identifier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.loan', to_field='identifier')),
            ],
            options={
                'verbose_name': 'Cash Flow',
                'verbose_name_plural': 'Cash Flows',
            },
        ),
    ]
