from django.shortcuts import render, redirect
from .models import *
from hashlib import sha1
from django.http import JsonResponse, HttpResponseRedirect
from . import user_decorator
from df_goods.models import *


def register(request):
    return render(request, 'df_user/register.html')


def register_handle(request):
    # 使用post请求接收用户输入
    # get用于纯粹的获取资源，post还可以用来改变数据
    post = request.POST
    uname = post.get('user_name')
    upwd = post.get('pwd')
    upwd2 = post.get('cpwd')
    uemial = post.get('email')
    # 判断两次密码
    if upwd != upwd2:
        # 重定向输入的是url里的元素
        return redirect('/user/register/')
    # 密码加密
    s1 = sha1()
    # 在python3中必须使用这个进行字符串的转码
    s1.update(upwd.encode("utf8"))
    upwd3 = s1.hexdigest()
    # 创建对象
    user = UserInfo()
    user.uname = uname
    user.upwd = upwd3
    user.uemail = uemial
    user.save()
    # 注册成功，转到登录页面
    return redirect('/user/login/')


def register_exist(request):
    uname = request.GET.get('uname')
    print(uname)
    count = UserInfo.objects.filter(uname=uname).count()
    return JsonResponse({'count': count})


def login(request):
    uname = request.COOKIES.get('uname', '')
    context = {'title': '用户登录', 'error_name': 0, 'error_pwd': 0, 'uname': uname}
    return render(request, 'df_user/login.html', context)


def login_handle(request):
    # 接收请求信息
    post = request.POST
    uname = post.get('username')
    upwd = post.get('pwd')
    jizhu = post.get('jizhu', 0)
    # 根据用户名查询对象
    users = UserInfo.objects.filter(uname=uname)
    print(uname)
    # 判断：如果未查询到则用户名错，如果查到则判断密码是否正确，正确则转到用户中心
    if len(users) == 1:
        s1 = sha1()
        s1.update(upwd.encode("utf8"))
        if s1.hexdigest() == users[0].upwd:
            # red = HttpResponseRedirect('/user/info/')
            # 如果用户在浏览前没有cookies缓存，就进去商城主页面
            # 如果用户在登录前已经浏览了该网站，就回到用户登录前的页面
            url = request.COOKIES.get('url', '/')
            red = HttpResponseRedirect(url)
            # 记住用户名
            if jizhu != 0:
                red.set_cookie('uname', uname)
            else:
                red.set_cookie('uname', '', max_age=-1)
            request.session['user_id'] = users[0].id
            request.session['user_name'] = uname
            return red
        else:
            context = {'title': '用户登录', 'error_name': 0, 'error_pwd': 1, 'uname': uname, 'upwd': upwd}
            return render(request, 'df_user/login.html', context)
    else:
        context = {'title': '用户登录', 'error_name': 1, 'error_pwd': 0, 'uname': uname, 'upwd': upwd}
        return render(request, 'df_user/login.html', context)


def logout(request):
    request.session.flush()
    return redirect('/')


@user_decorator.login
def info(request):
    user_email = UserInfo.objects.get(id=request.session['user_id']).uemail
    user_phone = UserInfo.objects.get(id=request.session['user_id']).uphone
    # 显示最近浏览记录，session在关闭网页时，内容全失效
    goods_ids = request.COOKIES.get('goods_ids', '')

    goods_ids1 = goods_ids.split(',')
    # 不要这样goodsInfo.objects.filter(id__in=goods_ids1),因为这样是直接根据
    # ID查询到的数据，数据不好处理
    goods_list = []
    for goods_id in goods_ids1:
        goods_list.append(GoodsInfo.objects.get(id=int(goods_id)))

    # 以上显示用户浏览记录
    context = {
        'title': '用户中心',
        'goods_list': goods_list,
        'page_name': 1,
        'user_email': user_email,
        'user_phone': user_phone,
        'user_name': request.session['user_name']}
    return render(request, 'df_user/user_center_info.html', context)


@user_decorator.login
def order(request):
    context = {'title': '用户中心', 'page_name': 1}
    return render(request, 'df_user/user_center_order.html', context)


@user_decorator.login
def site(request):
    user = UserInfo.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        post = request.POST
        user.ushou = post.get('ushou')
        user.uaddress = post.get('uaddress')
        user.uyoubian = post.get('uyoubian')
        user.uphone = post.get('uphone')
        user.save()
    context = {'title': '用户中心', 'page_name': 1, 'user': user}
    return render(request, 'df_user/user_center_site.html', context)
