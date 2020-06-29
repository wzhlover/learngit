from django.db import models


class CartInfo(models.Model):
    user = models.ForeignKey('df_user.UserInfo', null=True, blank=True, on_delete=models.SET_NULL)
    goods = models.ForeignKey('df_goods.GoodsInfo', null=True, blank=True, on_delete=models.SET_NULL)
    count = models.IntegerField()
# 谁买了什么东西
