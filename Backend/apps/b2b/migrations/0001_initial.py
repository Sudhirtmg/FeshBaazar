import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0003_user_b2b_fields'),
        ('shops', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ColdStorage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('address', models.TextField(blank=True)),
                ('verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='cold_storage',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'verbose_name_plural': 'Cold Storages'},
        ),
        migrations.CreateModel(
            name='ColdStorageProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('category', models.CharField(choices=[
                    ('chicken', 'Chicken'), ('beef', 'Beef'), ('buffalo', 'Buffalo'),
                    ('mutton', 'Mutton'), ('pork', 'Pork'), ('seafood', 'Seafood'), ('other', 'Other'),
                ], max_length=50)),
                ('allowed_units', models.JSONField(default=list, help_text="['kg'], ['piece'], or ['kg','piece']")),
                ('price_per_kg', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('stock_kg', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('low_stock_threshold', models.DecimalField(decimal_places=2, default=50, max_digits=10)),
                ('min_order_kg', models.DecimalField(blank=True, decimal_places=2, default=10, max_digits=8, null=True)),
                ('unit_type', models.CharField(
                    choices=[('kg', 'Kilogram'), ('piece', 'Piece')],
                    default='kg', max_length=10,
                    help_text='KG = price known upfront. Piece = price set after weighing.',
                )),
                ('approx_weight_per_piece_kg', models.DecimalField(
                    blank=True, decimal_places=3, max_digits=6, null=True,
                    help_text='Approximate kg per piece (informational only).',
                )),
                ('stock_pieces', models.PositiveIntegerField(
                    blank=True, null=True,
                    help_text='Available stock in pieces (used when unit_type=piece)',
                )),
                ('is_available', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cold_storage', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='products',
                    to='b2b.coldstorage',
                )),
            ],
        ),
        migrations.CreateModel(
            name='B2BOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(
                    choices=[
                        ('pending_price', 'Pending Price'), ('priced', 'Priced'),
                        ('pending', 'Pending'), ('confirmed', 'Confirmed'),
                        ('processing', 'Processing'), ('dispatched', 'Dispatched'),
                        ('delivered', 'Delivered'), ('cancelled', 'Cancelled'),
                    ],
                    default='pending', max_length=20,
                )),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, null=True)),
                ('paid_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('payment_type', models.CharField(
                    choices=[('cash', 'Cash'), ('credit', 'Credit')],
                    default='cash', max_length=10,
                )),
                ('order_source', models.CharField(
                    choices=[('app', 'App'), ('phone', 'Phone'), ('walkin', 'Walk-in')],
                    default='app', max_length=10,
                )),
                ('delivery_type', models.CharField(
                    choices=[('pickup', 'Pickup'), ('delivery', 'Delivery')],
                    default='pickup', max_length=10,
                )),
                ('delivery_address', models.TextField(blank=True)),
                ('delivery_latitude', models.FloatField(blank=True, null=True)),
                ('delivery_longitude', models.FloatField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cold_storage', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='incoming_orders',
                    to='b2b.coldstorage',
                )),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='created_orders',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('shop', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='b2b_orders',
                    to='shops.shop',
                )),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='B2BOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name_snapshot', models.CharField(max_length=255)),
                ('unit_type', models.CharField(
                    choices=[('kg', 'Kilogram'), ('piece', 'Piece')],
                    default='kg', max_length=10,
                )),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity_kg', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('price_per_kg_snapshot', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('actual_weight_kg', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('price_per_kg_final', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('line_total', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('order', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items',
                    to='b2b.b2border',
                )),
                ('product', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='order_items',
                    to='b2b.coldstorageproduct',
                )),
            ],
        ),
        migrations.CreateModel(
            name='B2BOrderStatusHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_status', models.CharField(blank=True, max_length=30)),
                ('to_status', models.CharField(max_length=30)),
                ('note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('changed_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                )),
                ('order', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='history',
                    to='b2b.b2border',
                )),
            ],
            options={'ordering': ['created_at']},
        ),
        migrations.CreateModel(
            name='LedgerEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('balance_after', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('entry_type', models.CharField(
                    choices=[('credit', 'Credit (Udhar Given)'), ('payment', 'Payment Received')],
                    max_length=10,
                )),
                ('note', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cold_storage', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='b2b.coldstorage',
                )),
                ('collected_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='collected_entries',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('weighted_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='weighted_entries',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('order', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    to='b2b.b2border',
                )),
                ('shop', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='shops.shop',
                )),
            ],
        ),
    ]
