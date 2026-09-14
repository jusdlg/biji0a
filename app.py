



from flask import Flask, render_template, request, url_for, session, redirect
from datetime import datetime
import db
from wrapper import login_required, admin_required

try:
     db.exec_sql("alter table user add is_admin integer default 0")
except Exception as e:
     print("字段已存在，跳过：",e)
db.exec_sql("update user set is_admin=1 where name='222'")

app = Flask(__name__)

app.config['SECRET_KEY']="fdlsjkafjieri6981"

from flask import Blueprint
user = Blueprint("user",__name__,url_prefix="/user")
@user.route("/show")
def show():
    return "show user"

app.register_blueprint(user)


#用户部分
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    del session['id']
    return redirect(url_for("login"))

@app.route("/do_login",methods=["POST"])
def do_login():
    form = request.form
    name = form.get("name", "")
    password = form.get("password", "")
    result = db.query_sql("select * from user where name=? and password = ?", [name, password])

    if len(result)>0:#找到用户
        session['id']=result[0][0]
        session['is_admin'] = result[0][3]
        return redirect(url_for("index"))
    else:#找不到
        return render_template("login.html",errors="登录名或者密码错误")


@app.route("/register")
def register():
    return render_template("register.html")


def for_url(param):
    pass


@app.route("/do_register",methods=["POST"])
def do_register():
    form = request.form
    name = form.get("name","")
    password = form.get("password","")
    password2 = form.get("password2", "")
    if name=="" or password != password2:
        return render_template("register.html",errors="未填或密码不一致")

    db.exec_sql("insert into user(name,password) values (?,?)",[name,password])

    return redirect(url_for("login"))

@app.route("/change_password")
@login_required
def change_password():
    return render_template("change_password.html")

# 密码修改提交接口
@app.route("/do_change_password", methods=["POST"])
@login_required
def do_change_password():
    form = request.form
    old_pwd = form.get("old_password", "")
    new_pwd = form.get("new_password", "")
    new_pwd2 = form.get("new_password2", "")
    uid = session["id"]
    # 先校验原密码是否正确
    user = db.query_sql("select * from user where id=? and password=?", [uid, old_pwd])
    if len(user) <= 0:
        return render_template("change_password.html", errors="原密码不正确")
    if new_pwd != new_pwd2:
        return render_template("change_password.html", errors="两次新密码不一致")
    if new_pwd.strip() == "":
        return render_template("change_password.html", errors="新密码不能为空")
    # 更新密码
    db.exec_sql("update user set password=? where id=?", [new_pwd, uid])
    # 修改成功，跳回首页
    return redirect(url_for("index"))


@app.route("/change_name")
@login_required
def change_name():
    uid = session["id"]
    user = db.query_sql("select name from user where id=?", [uid])
    return render_template("change_name.html", username=user[0][0])

@app.route("/do_change_name",methods=["POST"])
@login_required
def do_change_name():
    form = request.form
    new_name = form.get("new_name","").strip()
    uid = session["id"]
    if new_name == "":
        return render_template("change_name.html",errors="用户名不能为空")
    # 判断新名字有没有被别人占用
    repeat = db.query_sql("select id from user where name=? and id<>?",[new_name,uid])
    if len(repeat)>0:
        return render_template("change_name.html",errors="该用户名已经被占用")
    db.exec_sql("update user set name=? where id=?",[new_name,uid])
    return redirect(url_for("index"))



#博客部分
@app.route("/add")
@login_required
def add():
    return render_template("add.html")

@app.route("/do_add",methods=["POST"])
@login_required
def do_add():
    form = request.form
    title = form.get("title","")
    content = form.get("content","")
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.exec_sql("insert into blog(title,content,uid,publish_time) values(?,?,?,?)",[title,content,session['id'],now_time])
    return redirect(url_for("index"))

@app.route("/delete")
@login_required
def delete():
    args = request.args
    id = args.get("id","")

    db.exec_sql("delete from blog where id = ?", [id])

    return redirect(url_for("index"))

@app.route("/edit")
@login_required
def edit():
    args = request.args
    id = args.get("id", "")

    data = db.query_sql("select * from blog where id =?", [id])

    return render_template("edit.html",blog=data[0])

@app.route("/do_edit",methods=['POST'])
@login_required
def do_edit():
    form = request.form
    id = form.get("id","")
    title = form.get("title","")
    content = form.get("content","")
    #编辑不更新发布时间
    db.exec_sql("update blog set title=?, content=? where id=?",[title,content,id])
    return redirect(url_for("index"))

@app.route("/")
@login_required

def index():
    args = request.args
    key = args.get("key","")
    page =int(args.get("page","1"))
    number_per_page=2
    if page <1:
        page=1


    blogs = db.query_sql("select * from blog where (title like ? or content like ?)and uid = ? order by id desc limit?,?",
                        [f"%{key}%",f"%{key}%",session['id'],(page-1)*number_per_page,number_per_page])

    return render_template("index.html",blogs=blogs,page=page)

@app.route("/user_list")
@admin_required
def user_list():
    users = db.query_sql("select * from user")

    return render_template("user_list.html",users = users)

@app.route("/user_delete")
def user_delete():
    args =request.args
    id = int(args.get("id","0"))

    db.exec_sql("delete from user where id =?",[id])

    return redirect(url_for("user_list"))

if __name__ == "__main__":
    app.run(debug=True)