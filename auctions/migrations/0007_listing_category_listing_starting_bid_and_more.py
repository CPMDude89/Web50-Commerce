# Generated by Django 4.1.3 on 2022-11-30 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_alter_listing_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='category',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='listing',
            name='starting_bid',
            field=models.DecimalField(decimal_places=2, default=1000, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='listing',
            name='image',
            field=models.ImageField(blank=True, upload_to='auctions/'),
        ),
    ]
