from django.db import models

class KData(models.Model):
    date = models.CharField(primary_key=True, max_length=20)
    ts_code = models.CharField(max_length=10)
    open = models.FloatField(blank=True, null=True)
    close = models.FloatField(blank=True, null=True)
    high = models.FloatField(blank=True, null=True)
    low = models.FloatField(blank=True, null=True)
    vol = models.FloatField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'k_data'
        unique_together = (('date', 'ts_code'),)

class Latest(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    id = models.IntegerField(blank=True, null=True)
    datetime = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'latest'

class Senti(models.Model):
    datetime = models.CharField(primary_key=True, max_length=20)
    code = models.CharField(max_length=10)
    pos = models.IntegerField(blank=True, null=True)
    neg = models.IntegerField(blank=True, null=True)
    neu = models.IntegerField(blank=True, null=True)
    posscore = models.FloatField(blank=True, null=True)
    negscore = models.FloatField(blank=True, null=True)
    neuscore = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'senti'
        unique_together = (('datetime', 'code'),)

class SentiDaily(models.Model):
    datetime = models.CharField(primary_key=True, max_length=20)
    code = models.CharField(max_length=10)
    pos = models.IntegerField(blank=True, null=True)
    neg = models.IntegerField(blank=True, null=True)
    neu = models.IntegerField(blank=True, null=True)
    posscore = models.FloatField(blank=True, null=True)
    negscore = models.FloatField(blank=True, null=True)
    neuscore = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'senti_daily'
        unique_together = (('datetime', 'code'),)

class StockList(models.Model):
    ts_code = models.CharField(primary_key=True, max_length=10)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=10)
    industry = models.CharField(max_length=10)
    list_date = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'stock_list'

class Words(models.Model):
    datetime = models.CharField(primary_key=True, max_length=20)
    text = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'words'

class Settings(models.Model):
    item = models.CharField('配置项', max_length=256)
    value = models.TextField('值')
    update_time = models.DateTimeField('修改日期',auto_now=True, null=True)

    class Meta:
        managed = True

    def __str__(self):
        return self.item