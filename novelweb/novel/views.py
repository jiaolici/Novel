from django.shortcuts import render,redirect,reverse
from django.urls import reverse
from .novelspider import spiderfactory
from .models import Novel,User,User_Collections,Novel_Comment,Circle,User_Circle,Post,Post_Reply,Recommend,Message
from django.http import JsonResponse,HttpResponseRedirect
from django.db.models import Q,F
from django.db.utils import IntegrityError
from django.core.mail import send_mail
import random,datetime
# Create your views here.
source = '新笔趣阁'
Email_verificode_register={}
Email_verificode_passwordChange={}
def index(request):
    spider = spiderfactory.getSpider('http://zongheng.com')
    recommends = spider.getRecommend()
    try:
        user = User.objects.get(id=request.session.get('id'))
    except:
        user=None
    type1=Novel.objects.filter(novel_type='玄幻',source=source)[0:4]
    type2=Novel.objects.filter(novel_type='修真',source=source)[0:4]
    type3=Novel.objects.filter(novel_type='都市',source=source)[0:4]
    type4=Novel.objects.filter(novel_type='穿越',source=source)[0:4]
    type5=Novel.objects.filter(novel_type='网游',source=source)[0:4]
    type6=Novel.objects.filter(novel_type='科幻',source=source)[0:4]
    k1 = ('玄幻', type1)
    k2 = ('修真', type2)
    k3 = ('都市', type3)
    k4 = ('穿越', type4)
    k5 = ('网游', type5)
    k6 = ('科幻', type6)
    context = {'novellist':[k1,k2,k3,k4,k5,k6],
             'recommends':recommends,
               'user':user
             }
    return render(request,'novel/index.html',context=context)

def getNovelInfo(request):
    infourl = request.GET.get('infourl', None)
    novelid = request.GET.get('novelid', None)
    spider = spiderfactory.getSpider(infourl)
    chapters = spider.getChapters(infourl)
    novel = Novel.objects.filter(pk=int(novelid)).get()
    try:
        user = User.objects.get(id=request.session.get('id'))
    except:
        user=None
    if (chapters and chapters[-1]['title']!=novel.last_update_chapter):
        novel.last_update_chapter = chapters[-1]['title']
        novel.last_update_time = datetime.datetime.now()
        novel.save()
        ucs = User_Collections.objects.filter(novel=novel)
        for i in ucs:
            content = "小说《"+\
                      novel.name+\
                      "》更新到了<a href='/novel/getContent?chapterUrl="+\
                      chapters[-1]['chapterUrl']+\
                      "&novelname="+\
                      novel.name+\
                      "&chaptername="+ \
                      novel.last_update_chapter+\
                      "&novelid="+\
                      str(novel.id)+\
                      "' style='margin-left:3px;margin-right:3px;color:#1E9FFF'>"+\
                      novel.last_update_chapter+\
                      "</a>!"
            message = Message(user=i.user,msg_type='小说更新',title='您收藏的小说《'+novel.name+'》更新了！',content=content)
            message.save()
    try:
        user_collection = User_Collections.objects.get(user=user, novel=novel)
    except:
        user_collection = None
    all_novels = Novel.objects.raw('SELECT * FROM novel WHERE name=%s AND author=%s',[novel.name,novel.author])
    all_sources = []
    for i in all_novels:
        all_sources.append(i)
    context = {'chapters': chapters, 'novel': novel,'all_sources':all_sources,'user':user}
    if (user_collection):
        context['is_collected'] = True
    else:
        context['is_collected'] = False
    comments = Novel_Comment.objects.filter(novel=novel,comment=None)
    context['comments'] = comments
    return render(request, 'novel/novelInfo.html', context)

def getContent(request):
    chapterUrl=request.GET.get('chapterUrl',None)
    novelname=request.GET.get('novelname',None)
    chaptername=request.GET.get('chaptername',None)
    novelid=request.GET.get('novelid',None)
    spider= spiderfactory.getSpider(chapterUrl)
    content=spider.getChapterContent(chapterUrl)
    novel = Novel.objects.get(id=novelid)
    infoUrl=novel.novel_url

    sections = content.split('<br>')
    while '' in sections:
        sections.remove('')
    for i in range(len(sections)):
        sections[i] = sections[i].replace('&ensp;','')
    context={'content':content,
             'sections':sections,
             'chaptername':chaptername,
             'novelname':novelname,
             'infoUrl':infoUrl,
             'chapterUrl':chapterUrl,
             'novelid':novelid,
             }
    return render(request, 'novel/chapterContent.html',context )

def preChapter(request):
    infoUrl = request.GET.get('infoUrl', None)
    chapterUrl = request.GET.get('chapterUrl', None)
    novelname = request.GET.get('novelname', None)
    novelid = request.GET.get('novelid', None)
    spider = spiderfactory.getSpider(infoUrl)
    chapters = spider.getChapters(infoUrl)
    preUrl = chapters[0].get('chapterUrl')
    title = chapters[0].get('title')
    for i in range(1, len(chapters)):
        if chapterUrl == chapters[i].get('chapterUrl'):
            preUrl = chapters[i - 1].get('chapterUrl')
            title = chapters[i - 1].get('title')
            break

    content = spider.getChapterContent(preUrl)
    context = {"content": content,
               'chaptername': title,
               'novelname': novelname,
               'infoUrl': infoUrl,
               'chapterUrl': preUrl,
               'novelid': novelid,
               }
    return render(request, 'novel/chapterContent.html', context)

def nextChapter(request):
    infoUrl = request.GET.get('infoUrl', None)
    chapterUrl = request.GET.get('chapterUrl', None)
    novelname = request.GET.get('novelname', None)
    novelid = request.GET.get('novelid', None)
    spider = spiderfactory.getSpider(infoUrl)
    chapters = spider.getChapters(infoUrl)
    nextUrl = chapters[len(chapters)-1].get('chapterUrl')
    title = chapters[len(chapters)-1].get('title')
    for i in range(0, len(chapters)):
        if chapterUrl == chapters[i].get('chapterUrl'):
            nextUrl = chapters[i + 1].get('chapterUrl')
            title = chapters[i + 1].get('title')
            break

    content = spider.getChapterContent(nextUrl)
    context = {"content": content,
               'chaptername': title,
               'novelname': novelname,
               'infoUrl': infoUrl,
               'chapterUrl': nextUrl,
               'novelid': novelid,
               }
    return render(request, 'novel/chapterContent.html', context)

def indexMore(request):
    typenum = request.POST.get('typenum', None)
    page = request.POST.get('page', None)
    typenum = int(typenum)
    page = int(page)
    if(typenum==0):
        novels = Novel.objects.filter(novel_type='玄幻',source=source)
    elif(typenum==1):
        novels = Novel.objects.filter(novel_type='修真', source=source)
    elif(typenum==2):
        novels = Novel.objects.filter(novel_type='都市', source=source)
    elif(typenum==3):
        novels = Novel.objects.filter(novel_type='穿越', source=source)
    elif(typenum==4):
        novels = Novel.objects.filter(novel_type='网游', source=source)
    elif(typenum==5):
        novels = Novel.objects.filter(novel_type='科幻', source=source)
    novels = novels[4 + (page - 1) * 8:4 + page * 8]
    context = {'novels': list(novels.values()),
               }
    return JsonResponse(context)

def search(request):
    keyword = request.GET.get('kw', None)
    for spider in spiderfactory.getAllSpider():
        novels = spider.getSearch(keyword=keyword)
        for novel in novels:
            model = Novel(**novel)
            try:
                model.save()
            except IntegrityError:
                pass
    novel_list = Novel.objects.filter(Q(author__contains=keyword) | Q(name__contains=keyword))
    context = {'novel_list': novel_list,'catalog':'查找结果'}
    return render(request, 'novel/showNovels.html',context=context)

def login(request):
    Email = request.POST.get('Email')
    password = request.POST.get('password')
    try:
        user = User.objects.get(Email=Email,password=password)
    except:
        user = None
    if user:
        request.session['id'] = user.id
        return JsonResponse({'status':'登录成功'})#redirect('/novel')#return redirect(reverse('index',args=(user,)))
    else:
        return JsonResponse({'status':'登陆失败'})

def getverificode(request):
    email = request.POST.get('Email', None)
    verificode = random.randrange(1000,10000)
    message='尊敬的用户'+email+',您好：'\
            +'\n您的绑定验证码是：'+str(verificode)\
            +'\n本邮件由系统自动发送，请勿直接回复！'\
            +'\n感谢您的访问，祝您使用愉快！'
    try:
        user = User.objects.get(Email=email)
    except:
        user = None
    if not user and request.path=="/novel/getverificode_passwordChange":
        return JsonResponse({'status': '用户不存在!'})
    res = send_mail(subject='流溪阁--邮箱验证', message=message, from_email='流溪阁在线小说<1321869892@qq.com>',recipient_list=[email], fail_silently=False)
    context={}
    if(res==0):
        context = {'status': '失败'}
    elif(res==1):
        context = {'status': '成功'}
        if(request.path=="/novel/getverificode_register"):
            Email_verificode_register[email]=verificode
        elif(request.path=="/novel/getverificode_passwordChange"):
            Email_verificode_passwordChange[email]=verificode
    return JsonResponse(context)

def register(request):
    if request.method=='GET':
        return render(request, 'novel/register.html')
    username = request.POST.get('username',None)
    password = request.POST.get('password',None)
    Email = request.POST.get('Email',None)
    Email_vc = request.POST.get('Emailverificationcode',None)
    context = {}
    if(Email_vc != str(Email_verificode_register.get(Email))):
        context = {'status':'注册失败,验证码错误'}
        return JsonResponse(context)
    try:
        model = User(user_name=username,password=password,Email=Email)
        model.save()
    except IntegrityError:
        context = {'status': '注册失败,用户已存在'}
        return JsonResponse(context)
    else:
        context = {'status': '注册成功!'}
        return JsonResponse(context)

def collect(request):
    novelid = request.POST.get('novelid',None)
    collect = request.POST.get('collect',None)
    try:
        user = User.objects.get(id=request.session.get('id',None))
    except:
        user = None
    try:
        novel = Novel.objects.get(id=novelid)
    except:
        novel = None
    try:
        user_collection = User_Collections.objects.get(user=user,novel=novel)
    except:
        user_collection = None
    if(collect=='true'):
        if(user_collection):
            user_collection.delete()
            return JsonResponse({'message': '取消收藏成功!'})
    else:
        if(not user_collection and user):
            user_collection = User_Collections(user=user,novel=novel)
            user_collection.save()
            return JsonResponse({'message': '收藏成功!'})
        elif(not user_collection and not user):
            return JsonResponse({'message':'请先登录哦!'})

def logout(request):
    if request.session.get('id',None):
        del request.session['id']
    return HttpResponseRedirect('/novel')

def mycollections(request):
    userid = request.session.get('id', None)
    try:
        user = User.objects.get(id=userid)
    except:
        user = None
    try:
        user_collections = User_Collections.objects.filter(user=user)
    except:
        user_collections = []
    novels = []
    for user_collection in user_collections:
        novels.append(user_collection.novel)
    context = {'novel_list': novels, 'catalog': '我的收藏'}
    return render(request, 'novel/showNovels.html', context=context)

def passwordChange(request):
    if request.method=='GET':
        return render(request, 'novel/passwordChange.html')
    password = request.POST.get('password', None)
    Email = request.POST.get('Email', None)
    Email_vc = request.POST.get('Emailverificationcode', None)
    context = {}
    if (Email_vc != str(Email_verificode_passwordChange.get(Email))):
        context = {'status': '修改失败，验证码错误!'}
        return JsonResponse(context)
    try:
        user = User.objects.get(Email=Email)
    except:
        user = None
    if user:
        user.password = password
        user.save()
        try:
            del request.session['id']
        except:
            pass
        context = {'status': '修改成功!'}
        return JsonResponse(context)
    else:
        context = {'status': '修改失败，用户不存在'}
        return JsonResponse(context)

def rank(request):
    return render(request,'novel/rank.html')

def findRecommend(request):
    userid = request.session.get('id', None)
    try:
        user = User.objects.get(id=userid)
    except:
        user = None
    recommends = Recommend.objects.all().order_by('-pub_time')
    context={'user':user,'recommends':list(recommends)}
    return render(request,'novel/find_recommend.html',context=context)

def findMsg(request):
    userid = request.session.get('id', None)
    messages = []
    try:
        user = User.objects.get(id=userid)
    except:
        user = None
    try:
        messages.extend(list(Message.objects.filter(user=user).order_by('-pub_time')))
    except:
        pass
    context = {'user':user,'messages':messages}
    return render(request, 'novel/find_msg.html',context=context)

def findCircle(request):
    userid = request.session.get('id', None)
    try:
        user = User.objects.get(id=userid)
    except:
        user = None
    circle_name = request.GET.get('circle',None)
    kw = request.GET.get('kw',None)
    circles = []
    posts_and_replys = []
    posts = Post.objects.none()
    if(circle_name and kw):
        return HttpResponseRedirect('/novel/findCircle')
    elif(circle_name):
        circles.append(Circle.objects.get(circle_name=circle_name))
    elif(kw):
        circles.extend(list(Circle.objects.filter(Q(circle_name__contains=kw) | Q(interpretation__contains=kw))))
        print('xxxx')
    else:
        try:
            user_circles = User_Circle.objects.filter(user=user)
        except:
            user_circles = []
        for user_circle in user_circles:
            circles.append(user_circle.circle)
    print(circles)
    for circle in circles:
        posts = posts | Post.objects.filter(circle=circle).order_by('-pub_time')
    for post in posts:
        post_replys = Post_Reply.objects.filter(post=post,reply=None).order_by('-pub_time')
        posts_and_replys.append((post,post_replys,len(post_replys)))
    context = {'user': user}
    context['posts_and_replys']=posts_and_replys
    context['circles'] = circles
    return render(request, 'novel/find_circle.html',context=context)

def postlayer(request):
    # if request.method == 'GET':
    #     options=[]
    #     for n in set:
    #         options.append({'key':key,'txt':txt})
    #     return render(request,'postlayer.html',{'options':options})
    pass

def pubComment(request):
    novelid = request.POST.get('novelid',None)
    content = request.POST.get('content',None)
    commentid = request.POST.get('commentid',None)
    pub_time = request.POST.get('pub_time',None)
    userid = request.session.get('id', None)
    try:
        user = User.objects.get(id=userid)
    except:
        user = None
    try:
        novel = Novel.objects.get(id=novelid)
    except:
        novel = None
    try:
        comment = Novel_Comment.objects.get(id=commentid)
    except:
        comment = None
    if not user or not novel or not content or not pub_time:
        return JsonResponse({'status':'false'})
    novel_comment = Novel_Comment(user=user,novel=novel,content=content,pub_time=pub_time,praise=0,comment=comment)
    novel_comment.save()
    if(comment):
        message = Message(user=comment.user,msg_type='用户回复',title='有人回复了你！',content="用户 "+user.user_name+" 在小说 《"+novel.name+"》 下回复了你： "+content)
        message.save()
    return JsonResponse({'status':'true','comment_id':novel_comment.id})

def getCommentReply(request):
    commentid = request.POST.get('commentid',None)
    try:
        comment = Novel_Comment.objects.get(id=commentid)
    except:
        comment = None
    replys = getAllComment(comment)
    replys = list(replys)
    del replys[0]
    replys1 = []
    for reply in replys:
        replys1.append(
            {'id': reply.id, 'novel': reply.novel.id, 'user': reply.user.user_name, 'comment': reply.comment.user.user_name,
             'content': reply.content, 'pub_time': convertime(reply.pub_time), 'praise': reply.praise})

    return JsonResponse({'comment_replys':replys1})

def getAllComment(root):
    if not Novel_Comment.objects.filter(comment=root).exists():
        return Novel_Comment.objects.none() | Novel_Comment.objects.filter(id = root.id)#新建一个空queryset对象然后合并
    result = Novel_Comment.objects.none()
    result=result | Novel_Comment.objects.filter(id = root.id)
    for child in Novel_Comment.objects.filter(comment=root):
        result = result | getAllComment(child)
    return result

def novelCommentPraise(request):
    return JsonResponse({})

def createCircle(request):
    userid = request.session.get('id', None)
    try:
        user = User.objects.get(id=userid)
    except:
        user = None
    name = request.POST.get('name',None)
    interpretation = request.POST.get('interpretation',None)
    try:
        circle = Circle(circle_name=name,interpretation=interpretation)
        circle.save()
        user_circle = User_Circle(user=user,circle=circle)
        user_circle.save()
        return JsonResponse({'status':'成功'})
    except:
        return JsonResponse({'status':'失败'})

def pubPost(request):
    title = request.POST.get('title',None)
    content = request.POST.get('content', None)
    circle_name = request.POST.get('circle_name', None)
    userid = request.session.get('id', None)
    try:
        user = User.objects.get(id=userid)
    except:
        user = None
    try:
        circle = Circle.objects.get(circle_name=circle_name)
    except:
        circle=None
    try:
        post = Post(user=user,circle=circle,title=title,content=content,praise=0,shared=0)
        post.save()
        return JsonResponse({'status': '成功'})
    except:
        return JsonResponse({'status': '失败'})

def pubPostReply(request):
    content = request.POST.get('content',None)
    post_id = request.POST.get('post_id',None)
    userid = request.session.get('id', None)
    try:
        user = User.objects.get(id=userid)
    except:
        user = None
    try:
        post = Post.objects.get(id=post_id)
    except:
        post=None
    try:
        post_reply = Post_Reply(user=user,post=post,content=content,praise=0)
        post_reply.save()
        message = Message(user=post.user, msg_type='用户回复', title='有人回复了你的贴子！',
                          content="用户 " + user.user_name + " 在你的贴子 "+post.title+" 回复了你： " + content)
        message.save()
        return JsonResponse({'status':'成功'})
    except:
        return JsonResponse({'status': '失败'})

def pubPostReplyReply(request):
    content = request.POST.get('content',None)
    reply_id = request.POST.get('reply_id',None)
    userid = request.session.get('id', None)
    try:
        user = User.objects.get(id=userid)
    except:
        user = None
    try:
        to_reply = Post_Reply.objects.get(id=reply_id)
    except:
        to_reply = None
    try:
        reply = Post_Reply(user=user,post=to_reply.post,reply=to_reply,content=content,praise=0)
        reply.save()
        message = Message(user=to_reply.user, msg_type='用户回复', title='有人回复了你！',
                          content="用户 " + user.user_name + " 在贴子 " + to_reply.post.title + " 下回复了你： " + content)
        message.save()
        return JsonResponse({'status':'成功'})
    except:
        return JsonResponse({'status':'失败'})

def getPostReplyReply(request):
    reply_id = request.POST.get('reply_id',None)
    try:
        reply = Post_Reply.objects.get(id=reply_id)
    except:
        reply = None
    replys = getAllPostReply(reply)
    replys = list(replys)
    del replys[0]
    replys1 = []
    for reply in replys:
        replys1.append({'id':reply.id,'post':reply.post.id,'user':reply.user.user_name,'reply':reply.reply.user.user_name,'content':reply.content,'pub_time':convertime(reply.pub_time),'praise':reply.praise})

    return JsonResponse({'replys': replys1})

def getAllPostReply(root):
    if not Post_Reply.objects.filter(reply=root).exists():
        return Post_Reply.objects.none() | Post_Reply.objects.filter(id = root.id)#新建一个空queryset对象然后合并
    result = Post_Reply.objects.none()
    result=result | Post_Reply.objects.filter(id = root.id)
    for child in Post_Reply.objects.filter(reply=root):
        result = result | getAllPostReply(child)
    return result

def getCircle(request):
    circle_name = request.POST.get('circle_name',None)
    userid = request.session.get('id', None)
    try:
        user = User.objects.get(id=userid)
    except:
        user = None
    try:
        circle = Circle.objects.get(circle_name=circle_name)
    except:
        circle = None
    try:
        user_circle = User_Circle.objects.get(user=user,circle=circle)
    except:
        user_circle = None
    return JsonResponse({'interpretation': circle.interpretation,'is_joined':'是' if user_circle else '否'})

def joinCircle(request):
    circle_name = request.POST.get('circle_name', None)
    userid = request.session.get('id', None)
    try:
        user = User.objects.get(id=userid)
    except:
        user = None
    try:
        circle = Circle.objects.get(circle_name=circle_name)
    except:
        circle = None
    try:
        user_circle = User_Circle.objects.get(user=user,circle=circle)
    except:
        user_circle = None
    if(not user):
        return JsonResponse({'status': '请先登录哦！'})
    if(user_circle):
        user_circle.delete()
        return JsonResponse({'status':'退出圈子成功！'})
    else:
        user_circle = User_Circle(user=user, circle=circle)
        user_circle.save()
        return JsonResponse({'status':'加入圈子成功！'})

def pubRecommend(request):
    novel_name = request.POST.get('novel_name')
    author = request.POST.get('author')
    reason = request.POST.get('reason')
    userid = request.session.get('id', None)
    try:
        user = User.objects.get(id=userid)
    except:
        user = None
    if(not user):
        return JsonResponse({'msg':'请先登录哦！'})
    else:
        try:
            novel = Novel.objects.get(name=novel_name,author=author)
        except:
            novel = None
        if(not novel):
            return JsonResponse({'msg': '未找到相关小说！'})
        else:
            try:
                recommend = Recommend(novel=novel,user=user,reason=reason,praise=0,tread=0)
                recommend.save()
                return JsonResponse({'msg':'发布成功！'})
            except:
                return JsonResponse({{'msg':'发布失败！'}})

def latest(request):
    now = datetime.datetime.now()
    start = now - datetime.timedelta(days=7)
    novel_list = Novel.objects.filter(last_update_time__gte=start).order_by('-last_update_time')
    context = {'novel_list': novel_list, 'catalog': '最近更新'}
    return render(request, 'novel/showNovels.html', context=context)

def finished(request):
    novel_list = Novel.objects.filter(status=True)
    context = {'novel_list': novel_list, 'catalog': '已完结'}
    return render(request, 'novel/showNovels.html', context=context)

def convertime(datetime):
    return  ('%s年%s月%s日 %s:%s' % (datetime.strftime('%Y'), datetime.strftime('%m'),datetime.strftime('%d'), datetime.strftime('%H'),datetime.strftime('%M')))

def test(request):
    return render(request,'novel/search.html')