# app.py (完整逻辑版)
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename # 用于让文件名更安全

app = Flask(__name__)

# 配置上传路径
app.config['UPLOAD_FOLDER'] = 'static/uploads'
# 配置数据库文件
DATABASE = 'notebook.db'

# --- 数据库初始化函数 ---
def init_db():
    # 连接数据库 (如果不存在会自动创建)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # 创建表：存 ID, 标题, 内容, 图片文件名
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            image_filename TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 每次启动前先检查数据库是否存在
if not os.path.exists(DATABASE):
    init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 1. 拿数据
        title = request.form['title']
        content = request.form['content']
        image = request.files['image']
        
        filename = ""
        # 2. 处理图片保存
        if image:
            # secure_filename 把 "我的图片.jpg" 变成 "My_Picture.jpg" 避免乱码
            filename = secure_filename(image.filename)
            # 保存到 static/uploads/ 文件夹
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # 3. 存入数据库
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO posts (title, content, image_filename) VALUES (?, ?, ?)',
                       (title, content, filename))
        conn.commit()
        conn.close()
        
        # 4. 存完之后，跳转到一个新页面（查看数据页）
        # 注意：这里我们还没写 'data_page'，等下个阶段写
        return redirect('/data')

    return render_template('index.html')


@app.route('/data')
def data_page():
    # 1. 连接数据库
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 2. 查询所有数据 (按 ID 倒序，最新的在前面)
    cursor.execute('SELECT * FROM posts ORDER BY id DESC')
    results = cursor.fetchall() # 拿到所有结果列表
    conn.close()
    
    # 3. 把结果传给 HTML
    return render_template('data.html', posts=results)

if __name__ == '__main__':
    app.run(debug=True)