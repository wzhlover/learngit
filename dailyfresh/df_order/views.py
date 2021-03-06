from django.shortcuts import render,redirect
from df_cart.models import CartInfo
from df_user import user_decorator
from .models import *
from django.db import transaction
from datetime import datetime
from decimal import Decimal


@user_decorator.login
def order(request):
    # 查询用户对象
    user = UserWarning.objects.get(id=request.session['user_id'])
    # 根据提交查询购物车信息
    get = request.GET
    cart_ids = get.getlist('cart_id')
    cart_ids1 = [int(item) for item in cart_ids]
    carts = CartInfo.objects.filter(id__in=cart_ids1)
    # 构造传递到模板中的数据
    context = {
        'title': '提交订单',
        'page_name': 1,
        'carts': carts,
        'user': user,
        'cart_ids': ','.join(cart_ids)}
    return render(request, 'df_order/order.html', context)

"""
事务：一旦操作失败则全部回退
1、创建订单对象
2、判断商品的库存
3、创建详单对象
4、修改商品库存
5、删除购物车
"""


@transaction.atomic()
@user_decorator.login
def order_handle(request):
    # 保存一个点
    tran_id = transaction.savepoint()
    # 接收购物车编号
    cart_ids = request.POST.get('cart_ids')
    try:
        # 创建订单对象
        order = OrderInfo()
        now = datetime.now()
        uid = request.session['user_id']
        order.oid = '%s%d' % (now.strftime('%Y%m%d%H%M%S'), uid)
        order.user_id = uid
        order.odate = now
        order.ototal = Decimal(request.POST.get('total'))
        order.save()
        # 创建详单对象
        cart_ids1 = [int(item) for item in cart_ids.split(',')]
        for id1 in cart_ids1:
            detail = OrderDetailInfo()
            detail.order = order
            # 查询购物车信息
            cart = CartInfo.objects.get(id=id1)
            # 判断商品库存
            goods = cart.goods
            if goods.gkuncun >= cart.count:
                # 减少商品库存
                goods.gkucun = cart.goods.gkucun-cart.count
                goods.save()
                # 完善详单信息
                detail.goods_id = goods.id
                detail.price = goods.gprice
                detail.count = cart.count
                detail.save()
                # 删除购物车数据
                cart.delete()
            else:  # 如果库存小于购买数量
                transaction.savepoint_rollback(tran_id)
                return redirect('/cart/')
        transaction.savepoint_commit(tran_id)
    except Exception as e:
        print("===============%s" % e)
        transaction.savepoint_rollback(tran_id)
    return redirect('/user/order/')


@user_decorator.login
def pay(request, oid):
    order = OrderInfo.objects.get(oid=oid)
    order.oIsPay = True
    order.save()
    context = {'order': order}
    return render(request, 'df_order/pay.html', context)
