import uiautomation as auto
import time,re,os,subprocess
from urllib.parse import urlparse, parse_qs
import pymysql
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import base64
auto.SetGlobalSearchTimeout(3)  # set new timeout 3

def countdown(tips,seconds):
    for i in range(seconds,0,-1):
        print(f"{tips}倒计时{i}")
        time.sleep(1)
        
def image_url_to_base64(image_url):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')
    except Exception as e:
        print(f"Error fetching cover image: {e}")
    return ""

def get_chrome_url():
    countdown('get chrome url',1)
    chrome = auto.WindowControl(searchDepth=1,ClassName='Chrome_WidgetWin_1',SubName='Google Chrome')
    if not chrome.Exists():
        chrome=auto.PaneControl(searchDepth=1,ClassName='Chrome_WidgetWin_1',SubName='Google Chrome')
    editControl_address=chrome.EditControl(name='地址和搜索栏')
    url=editControl_address.GetValuePattern().Value
    print(f"地址和搜索栏url为：{url},发送ctrl+w关闭")
    if url.startswith('mp.weixin.qq.com'):
        editControl_address.SendKeys('{Ctrl}{w}')
    return 'https://'+url

def upsert_gh_title(conn, i, gh_name, gh_title):
    cursor = conn.cursor()
    is_update_needed = False
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("SELECT last_title FROM account WHERE gh_name=%s", (gh_name,))
    db_title_fetchone = cursor.fetchone()    
    if db_title_fetchone is None:        # 如果公众号不存在，插入新记录
        cursor.execute("INSERT INTO account (gh_name, last_title, subscribe_time, update_time) VALUES (%s, %s, %s, %s)",(gh_name, gh_title, now, now))
        print(f"{now}   处理第{i}个,account库新增账号《{gh_name}》 ")
        is_update_needed = True
    else:        # 如果公众号存在，比较标题
        is_update_needed=False if db_title_fetchone[0]==gh_title else True
    conn.commit()
    cursor.close()
    return is_update_needed

def update_account_last_title(conn,gh_name,gh_title):
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("UPDATE account SET last_title=%s, update_time=%s WHERE gh_name=%s",(gh_title, now, gh_name))
    conn.commit()
    cursor.close()
    print(f"{now}   更新account库账号《{gh_name}》标题为《{gh_title}》成功！")


def single_file(url):
    single_file_path = "C:\\Program Files\\nodejs\\single-file.cmd"
    try:        # 构建完整的命令字符串，所有参数都用引号包裹        
        command = f'"{single_file_path}" "{url}" "--dump-content"'
        result = subprocess.run(command,check=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        html_content = result.stdout.decode('utf-8', errors='ignore')
        print(f"single-file下载成功，length={round(len(html_content)/(1024*1024),2)}MB")
        return html_content
    except subprocess.CalledProcessError as e:
        print(f"下载失败: {e.stderr}")
    except Exception as e:
        print(f"发生错误: {str(e)}")

def insert_mmreader_news(conn,gh_name,title,url):
    cursor=conn.cursor()    
    html_content=single_file(url)
    biz=parse_qs(urlparse(url).query).get('__biz', [None])[0]
    mid=parse_qs(urlparse(url).query).get('mid', [None])[0]
    idx=parse_qs(urlparse(url).query).get('idx', [None])[0]
    soup = BeautifulSoup(html_content, 'html.parser')
    og_title=soup.find('meta', property='og:title').get('content','')
    og_url = soup.find('meta', property='og:url').get('content', '')
    og_image = soup.find('meta', property='og:image').get('content', '')
    og_image_base64 = image_url_to_base64(og_image)
    og_description = soup.find('meta', property='og:description').get('content', '')
    og_site_name = soup.find('meta', property='og:site_name').get('content', '')
    og_type = soup.find('meta', property='og:type').get('content', '')
    og_article_author = soup.find('meta', property='og:article:author').get('content', '')
    twitter_card = soup.find('meta', property='twitter:card').get('content', '')
    twitter_image = soup.find('meta', property='twitter:image').get('content', '')
    twitter_image_base64 = image_url_to_base64(twitter_image)
    twitter_title = soup.find('meta', property='twitter:title').get('content', '')
    twitter_creator = soup.find('meta', property='twitter:creator').get('content', '')
    twitter_site = soup.find('meta', property='twitter:site').get('content', '')
    twitter_description = soup.find('meta', property='twitter:description').get('content', '')        
    content_clean = soup.get_text()
    publish_time = soup.find('em', id='publish_time').get_text()
    publish_time =  datetime.strptime(publish_time, "%Y年%m月%d日 %H:%M").strftime("%Y-%m-%d %H:%M:%S")
    #存入out今日文件夹
    date_dir = os.path.join(os.getcwd(), 'out', datetime.now().strftime('%Y%m%d'))
    os.makedirs(date_dir, exist_ok=True)
    now_time_str=datetime.now().strftime('%Y%m%d%H%M%S') 
    file_name = f"{gh_name}_{mid}-{idx}.html"
    file_path = os.path.join(date_dir, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML已保存到: {file_path} {file_name}")
    #插入mmreader
    insert_time = datetime.now()
    sql = f'''INSERT INTO mmreader (biz, mid, idx, gh_name, insert_time, title, url, publish_time, og_image, twitter_image, content_clean) 
    VALUES ('{biz}', '{mid}', {idx}, '{gh_name}', '{insert_time}', '{title}', '{url}', '{publish_time}', '{og_image_base64}', '{twitter_image_base64}', '{content_clean}')'''
    cursor.execute(sql)
    conn.commit()
    print(f"{now_time_str} {gh_name} 数据库插入文章详情成功: 《{title}》")  
    cursor.close()
      
def is_news_not_in_mmreader(conn,gh_name,title):
    cursor = conn.cursor()
    check_sql = f"SELECT COUNT(*) FROM mmreader WHERE gh_name = '{gh_name}' AND title = '{title}'"
    cursor.execute(check_sql)
    result = cursor.fetchone()
    cursor.close()
    if result[0] == 0:  
        print(f"检查{gh_name}新闻《{title}》    不存在，插入!")
        return True
    else:
        print(f"检查{gh_name}新闻《{title}》    已存在，不插!")
        return False
    
def get_news_list(conn,gh_name,gh_title):
    app=Chrome_RenderWidgetHostHWND.GroupControl(Depth=2,AutomationId='app')
    zhengzaijiazai=app.TextControl(searchDepth=6,Name='正在加载...')
    #print(f"正在加载...：{zhengzaijiazai.Name} ControlType={zhengzaijiazai.ControlType} ")
    gh_name_news=zhengzaijiazai.GetParentControl().GetChildren()
    count=len(gh_name_news)
    for index,zhengzaijiazai_brother in enumerate(gh_name_news,1):
        sub.SetActive()
        print(f"获取{gh_name}第{index}/{count}个新闻：{zhengzaijiazai_brother.Name} ")
        for article in zhengzaijiazai_brother.GetChildren():
            if(article.BoundingRectangle.width() == 0 or article.BoundingRectangle.height() == 0):
                print(f"第{index}个新闻控件不可见，且后续控件可能均不可见，终止循环")
                break  # 直接跳出整个for循环，不再处理后续控件
            if isinstance(article, auto.TextControl): #去掉“今天”，这种是GroupControl    
                count-=1
                continue
            elif isinstance(article, auto.GroupControl):               
                for article_title in article.GetChildren():     #文章标题、阅读数、图片三个循环
                    if isinstance(article_title, auto.TextControl):
                        title = article_title.Name
                        if is_news_not_in_mmreader(conn,gh_name,title):                         
                            print(f"新闻标题：（查看并右键点击）: {title}    clicking...")                   
                            article_title.RightClick()
                            countdown('article_title.RightClick',1)
                            liulanqidakai=zhengzaijiazai.GetParentControl().GetParentControl().GetParentControl().TextControl(searchDepth=3,Name='用默认浏览器打开')
                            print('找到浏览器打开菜单') if liulanqidakai.Exists() else print('未找到浏览器打开菜单')
                            liulanqidakai.Click()
                            countdown('liulanqidakai.Click',2)
                            insert_mmreader_news(conn,gh_name,title,get_chrome_url())
                        if title == gh_title:
                            update_account_last_title(conn,gh_name,gh_title)    

if __name__ == "__main__":
    while(True):
        countdown('程序main开启超级大循环,while(True) sleep 5',5)
        conn = pymysql.connect(host='localhost',user='root',passwd='nimazhale',database='zhiyue',charset='utf8mb4')
        sub = auto.WindowControl(searchDepth=1, ClassName='SubscriptionWnd', Name='订阅号')
        if not sub.Exists():
            print("订阅号窗口不存在或不可见，退出程序")
            exit()
        Chrome_WidgetWin_0 = sub.PaneControl(searchDepth=1, ClassName='Chrome_WidgetWin_0')
        Chrome_RenderWidgetHostHWND = Chrome_WidgetWin_0.DocumentControl(searchDepth=1, ClassName='Chrome_RenderWidgetHostHWND')
        group=Chrome_RenderWidgetHostHWND.GroupControl(Depth=4).GetChildren()
        for i, gh_item in enumerate(group,1):   #child是每个头像
            if gh_item.BoundingRectangle.width() == 0 or gh_item.BoundingRectangle.height() == 0:
                print(f"第{i}个头像控件不可见，且后续控件可能均不可见，终止循环")
                break  # 直接跳出整个for循环，不再处理后续控件
            if len(gh_item.GetChildren()) < 2:   # 如果被封账号没有新闻，去掉
                continue
            try:
                gh_name=gh_item.TextControl(searchDepth=1,foundIndex=1).Name
                gh_title=gh_item.TextControl(searchDepth=1,foundIndex=2).TextControl(searchDepth=1).Name
                print(f"获取第{i}个公众号：{gh_name}  控件最新标题：《{gh_title}》")
                is_update_needed=upsert_gh_title(conn,i,gh_name, gh_title)
                print(f"标题数据库更新检查{i}个     《{gh_name}》，is_update_needed={is_update_needed}")
                if is_update_needed:
                    print(f"控件检查第{i}个     《{gh_name}》有更新，新标题为：《{gh_title}》 ")
                    sub.SetActive()
                    countdown('点击了公众号，SetActive.',1)
                    gh_item.Click()
                    countdown('点击了公众号，进入新闻列表.Click',1)
                    get_news_list(conn,gh_name,gh_title)
                else:
                    print(f"控件检查第{i}个     《{gh_name}》，无更新！")    
            except Exception as e:
                print(f"这里错误太多了，Error occurred: {e}")
            if not conn:
                conn.close()