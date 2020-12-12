import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
#flaskの中のFlask、render_templateなどなどをインポートしている
from werkzeug.utils import secure_filename
app = Flask(__name__)

#画像のアップロード先のディエクトリ
UPLOAD_FOLDER = './uploads'
#アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])
#Flaskインスタンスのconfig変数に辞書形式で書き込む
#アプリの設定を行う
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(24)

def allowed_file(filename):
    #.がfilenameにあるかどうかのチェック
    #拡張子がALLOWED_EXTENSIONSのリストにあるものとあっているかの確認
    #拡張子はrsplitで分けたリストの二番目を[1]で取得することでわかる
    #適していればyesがreturnされる
    '''
    rsplitは今回の場合、filenameの右から一番目までを.があるところで分けて、リストにする
    ex) text = strawberry.banana.apple.grape
        text.rsplit(.,2)
        >>>["strawberry.banana","apple","grape"]
        #右から二番目までが.があるところで分けられた
    '''
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#ルーティング処理
'''
ルーティングとはURLと処理(function)を対応付けること
route()を用いる
'''
#この場合http://xxx/とindex()を結びつける
@app.route('/') # http://xxx以降のURLパスを'/'と指定
def index():
    #session内にusernameがあったら、index.htmlに移動
    if 'username' in session:
        return render_template('index.html')
    #でなければ、ログインしてくださいと表示する
    return '''
        <p>ログインしてください</p>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    #受け取ったhttpリクエストがPOSTだったら
    '''
    httpリクエストとは？
    webブラウザ(ソフト)がwebサーバー(ホームページ)にするお願い
    '''
    if request.method == 'POST':
        #POST送信されたパラメータを受け取る
        username = request.form['username']
        if username == 'admin':
            session['username'] = request.form['username']
            #index()のページに転送される
            return redirect(url_for('index'))
        else:
            return '''<p>ユーザー名が違います</p>'''

    #ユーザーネーム入れる欄とログインボタン作る
    return '''
        <form action="" method="post">
            <p><input type="text" name="username">
            <p><input type="submit" value="Login">
        </form>
    '''

@app.route('/logout')
def logout():
    #sessionの値をすべて削除
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        #img_fileに受け取ったファイル(request.files)を代入
        img_file = request.files['img_file']
        #img_fileがあり、かつallowed_fileがyesのときに実行
        if img_file and allowed_file(img_file.filename):
            filename = secure_filename(img_file.filename)
            #アップロードされたファイル(今回は写真)を保存
            #os.path.joinで引数に与えられた二つの文字列を結合させて、ひとつのパスにする
            img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #UPLOAD_FOLDERは./uploads
            img_url = '/uploads/' + filename
            return render_template('index.html', img_url=img_url)
        else:
            return ''' <p>許可されていない拡張子です</p> '''
    else:
        return redirect(url_for('index'))

#アップロードした画像にURLからアクセス
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.debug = True
    app.run()