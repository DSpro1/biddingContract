# Generated by Django 5.0.6 on 2024-07-20 23:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Fornecedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('cnpj', models.CharField(max_length=200)),
                ('endereco', models.CharField(max_length=200)),
                ('num', models.CharField(max_length=200)),
                ('bairro', models.CharField(max_length=200)),
                ('cep', models.CharField(max_length=200)),
                ('cidade', models.CharField(max_length=200)),
                ('telefone', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Licitacao',
            fields=[
                ('numProcess', models.IntegerField(primary_key=True, serialize=False)),
                ('categoria', models.CharField(max_length=200)),
                ('assunto', models.CharField(max_length=200)),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Contrato',
            fields=[
                ('numero', models.IntegerField(primary_key=True, serialize=False)),
                ('assuntoDetalhado', models.TextField(max_length=200)),
                ('dataInicial', models.DateField()),
                ('dataFinal', models.DateField()),
                ('valor', models.FloatField()),
                ('fornecedor_fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='biddingContracts.fornecedor')),
                ('licitacao_fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='biddingContracts.licitacao')),
            ],
        ),
        migrations.CreateModel(
            name='NotaFiscal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField()),
                ('serie', models.CharField(max_length=15)),
                ('valor', models.FloatField()),
                ('tipo', models.CharField(max_length=50)),
                ('contrato_fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='biddingContracts.contrato')),
            ],
            options={
                'verbose_name_plural': 'Notas Fiscais',
            },
        ),
    ]