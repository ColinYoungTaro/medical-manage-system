from flask import request, render_template, redirect, flash, url_for, jsonify, abort, Response
from flask_login import login_required
from flask_login import login_user, logout_user,current_user
from .models import Role
from . import main
from .models import db, User, permission_required, Auth
from flask_login import AnonymousUserMixin
from . import models as data
from sqlalchemy import func
from .form import Login

# 添加处方药函数
def add_prescription(kwargs):
    pres_list = data.Prescription(kwargs)
    maxcnt = db.session.query(func.max(data.Prescription.row_id)).first()[0]
    maxcnt += 1
    pres_list.row_id = maxcnt
    db.session.add(pres_list)
    db.session.commit()

# 删除处方药
def delete_prescription(row_id):
    if not current_user.can(Auth.DELETE) :
        flash('没有删除权限')
    prsc = data.Prescription.query.get(row_id)
    if(prsc):
        db.session.delete(prsc)
        db.session.commit()
    else:
        print("Data not exist")

#删除病人函数
def delete_patient(subject_id):
    record = data.Patient.query.get(subject_id)
    if(record):
        db.session.delete(record)
        db.session.commit()
    else:
        print("Data not exist")

# 获取所有病人实例
def get_all_subject_id():
    return data.Patient.query.all()

# 获取所有类型的药物
def get_all_drug():
    result = data.Prescription.query.with_entities(data.Prescription.drug).distinct().all()
    res = [iter[0] for iter in result]
    return res

# 获取所有用户
def get_users():
    return data.User.query.all()

def wrong_page():
    return "<h1>404</h1>"

# 将数据库结果格式转化为json格式以便于前后端交互
def mk_list(res):
    lst = []
    for row in res:
        dct = {}
        for key,val in row.__dict__.items():
            if not key.startswith('_sa_instance_state'):
                dct[key] = val
        lst.append(dct)
    return lst



# 路由列表：
# 登陆界面
@main.route('/login', methods=['GET', 'POST'])
def login():
    login_form = Login()
    if request.method == 'POST':
        password = login_form.password.data
        email = login_form.email.data
        user = User.query.filter_by(Email=email).first()
        print(password, email, user)
        if not user:
            flash('loginFailed')
        elif user.verify_password(password):
            print('login_success')
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            print("login_fail")
    return render_template('login2.html', form=login_form)


# 后台管理界面，通过排序和限制来显示数据
@main.route('/dataevents')
@login_required
@permission_required(Auth.READ)
def data_events():
    events = data.LabEvent.query.order_by(db.desc(data.LabEvent.charttime)).limit(1000)
    return render_template('dataevents.html',events = events)

# 后台管理界面，通过排序和限制来显示数据

@main.route('/patient-prec/<int:subject_id>')
@login_required
@permission_required(Auth.UPDATE)
def patient_presc(subject_id):
    presc = data.Prescription.query.filter_by(subject_id=subject_id).\
        order_by(db.desc(data.Prescription.startdate)).limit(100)
    return render_template('drug_info.html',presc = presc)

# 注册页面
@main.route('/doc-register', methods=['GET', 'POST'])
def doc_register():
    if request.method == 'POST':
        info = request.get_json()
        email = info['email']
        name = info['name']
        pwd = info['password']
        confirm_pwd = info['conform_password']
        print(email,name,pwd,confirm_pwd,"ABORT")
        if pwd != confirm_pwd:
            abort(500,Response('different password input'))
        else:
            res = User.query.filter_by(Email=email).first()
            if (res):
                abort(500,Response('email has been registered'))

        user = User(Email=email, name=name,role_id=14)
        user.password = pwd
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html')


# 删除病人函数
@main.route('/delete-patient',methods=['GET','POST'])
@permission_required(Auth.DELETE)
def delete_patient():
    if request.method == 'POST':
        if current_user.can(Auth.DELETE):
            msg = ['成功删除病人','success']
            print("Execute")
            data = request.get_json()
            delete_patient(data['data'])
        else:
            msg = ['删除失败','danger']
            print("FAIL")
    return ""

#
@main.route('/back-end-patients',methods=['POST','GET'])
def be_patients():
    msg = []
    return render_template('patients.html',patients=get_all_subject_id())
@main.route('/get-auth')
def get_auth():
    return current_user.can()
@main.route('/check-result')
@login_required
def main_interface():
    patient_list = get_all_subject_id()
    id = patient_list[0].subject_id
    return redirect(url_for('main.check_result',subject_id=id))

@main.route('/check-result/<int:subject_id>')
@login_required
@permission_required(Auth.READ)
def check_result(subject_id):
    ls = get_all_subject_id()
    admission = data.Admission.query.filter_by(subject_id=subject_id).first_or_404()
    patient = data.Patient.query.filter_by(subject_id=subject_id).first_or_404()
    drug_name_list = get_all_drug()
    return render_template('interface.html', select=patient, patients=ls, \
            admission=admission,user = current_user,drug_name_list = drug_name_list)


@main.route('/get-all-patients-number')
def getSubjId():
    ids = data.Patient.query.group_by('subject_id').subject_id



@main.route('/cpts')
@login_required
@permission_required(Auth.ADMIN)
def watchCPT():
    cpts = data.Cpt.query.all()

@main.route('/logout')
@login_required
def logout():
    print("logout")
    logout_user()  # 登出用户
    return redirect(url_for('main.index'))  # 重定向回首页


# 获取所有病人信息，并打包返回给前端
@main.route('/json')
def check_route():
    rs = data.Patient.query.all()
    json = mk_list(rs)
    return jsonify(json)

@main.route('/get_all_sjid_json')
def get_all_subject_json():
    res = list(get_all_subject_id())
    res = mk_list(res)
    return jsonify(res)

@main.route('/')
def index():

    print("currentUser:",current_user,current_user)
    html = render_template('index2.html',user=current_user)
    return html


def alter_prescription(row_id,attr_name,attr_val):
    pres= data.Prescription.query.get(row_id)
    if(not pres):
        return
    pres.__setattr__(attr_name,attr_val)
    db.session.commit()
    return pres

@main.route('/add-presc',methods=['GET','POST'])
def add_pres():
    if request.method == 'POST':
        if not current_user.can(Auth.UPDATE):
            abort(403)
        data = request.get_json()
        para = data['data']
        for iter in para:
            add_prescription(iter)

    return data



# 用户管理界面
@main.route('/user-list',methods=['GET','POST'])
@login_required
@permission_required(Auth.READ)
def user_list():
    if request.method == 'POST':
        if not current_user.can(Auth.ADMIN):
            abort(500)

        json_data = request.get_json()
        if json_data['func'] == 'alter':
            role_name = json_data['data']
            user_id = json_data['alter_user_id']
            role = Role.query.filter_by(name=role_name).first()
            id = role.id
            if user_id != 8 and current_user.can(Auth.ADMIN):
                # 测试用管理员id为8，不能删除
                user = data.User.query.filter_by(id=user_id).first()
                user.role_id = id
                db.session.commit()
        elif json_data['func'] == 'delete':
            if current_user.can(Auth.ADMIN):
                user_id = json_data['user_id']
                if user_id != 8 :
                    user = data.User.query.filter_by(id=user_id).first()
                    db.session.delete(user)
                    db.session.commit()
    userList = get_users()

    return render_template('users.html',user_list = userList)

# 获取所有处方药信息
@main.route('/get-pres/<int:subject_id>')
def query_prescription(subject_id):
    patient = data.Patient.query.filter_by(subject_id=subject_id).first_or_404()
    former_pres = patient.prescriptions
    lst = []
    for row in former_pres:
        dct = {}
        for k, v in row.__dict__.items():
            if not k.startswith('_sa_instance_state'):
                dct[k] = v
        lst.append(dct)
    db.session.commit()
    return jsonify(lst)

# 错误页面处理
@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403

