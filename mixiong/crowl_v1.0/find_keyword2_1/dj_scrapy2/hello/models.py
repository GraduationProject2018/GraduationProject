from django.db import models

# Create your models here.

class taskTable(models.Model):
    """
    subscribeStatus :订阅标志  0：不订阅
                        1：订阅
    status :0   任务未开始
            1   执行中
            2   完成
    """
    uid = models.CharField(max_length=50)

    url = models.CharField(max_length=100)
    domain = models.CharField(max_length=50)
    keyword = models.CharField(max_length=50)

    taskCreateDate = models.DateTimeField()
    subscribeStatus = models.IntegerField(default=0)
    status=models.IntegerField(default=0)

    class Meta:
        db_table = "pushTask"

class spiderkeyTable(models.Model):
    """

    """
    task=models.ForeignKey(taskTable)

    url=models.CharField(max_length=100)
    keyWordNum=models.IntegerField()

    modifiedTime=models.CharField(max_length=50)
    startTime=models.DateTimeField()
    class Meta:
        db_table="spiderKey"


