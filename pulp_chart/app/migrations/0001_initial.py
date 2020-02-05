# Generated by Django 2.2.10 on 2020-02-05 10:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0021_add_signing_service_foreign_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChartContent',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='chart_chartcontent', serialize=False, to='core.Content')),
            ],
            options={
                'default_related_name': '%(app_label)s_%(model_name)s',
            },
            bases=('core.content',),
        ),
        migrations.CreateModel(
            name='ChartPublication',
            fields=[
                ('publication_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='chart_chartpublication', serialize=False, to='core.Publication')),
            ],
            options={
                'default_related_name': '%(app_label)s_%(model_name)s',
            },
            bases=('core.publication',),
        ),
        migrations.CreateModel(
            name='ChartRemote',
            fields=[
                ('remote_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='chart_chartremote', serialize=False, to='core.Remote')),
            ],
            options={
                'default_related_name': '%(app_label)s_%(model_name)s',
            },
            bases=('core.remote',),
        ),
        migrations.CreateModel(
            name='ChartRepository',
            fields=[
                ('repository_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='chart_chartrepository', serialize=False, to='core.Repository')),
            ],
            options={
                'default_related_name': '%(app_label)s_%(model_name)s',
            },
            bases=('core.repository',),
        ),
        migrations.CreateModel(
            name='ChartDistribution',
            fields=[
                ('basedistribution_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='chart_chartdistribution', serialize=False, to='core.BaseDistribution')),
                ('publication', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chart_chartdistribution', to='core.Publication')),
            ],
            options={
                'default_related_name': '%(app_label)s_%(model_name)s',
            },
            bases=('core.basedistribution',),
        ),
    ]