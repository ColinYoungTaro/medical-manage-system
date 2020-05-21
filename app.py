import sys
sys.path.append('E:/DeskTopFiles/19-20/数据库/flask_proj')
sys.path.append('/home/flask_proj/DBSystem')
from flask import Flask
import os
from flask_bootstrap import Bootstrap

bootstrap = Bootstrap()

def create_app():
    app = Flask(__name__)
    from watchlist import main as main_blueprint
    hostname = "localhost"
    config_str = "mysql+pymysql://root:123456@"
    table_name = "tables"
    from watchlist.models import db
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = config_str + hostname + "/" + table_name
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    app.debug = True
    app.register_blueprint(main_blueprint)
    bootstrap.init_app(app)
    db.init_app(app)
    return app



from watchlist.models import db,User
import watchlist.models as data
from watchlist import views
from flask_script import Manager,Command,Shell
from flask_migrate import Migrate,MigrateCommand
from flask_cors import CORS,cross_origin


import click
from flask_login import LoginManager

# 基本配置
cors = CORS()
app = create_app()
cors.init_app(app=app, resources={r"/*": {"origins": "*"}})

manager = Manager(app)
migrate = Migrate(app,db)
login_manager = LoginManager(app)
manager.add_command('db',MigrateCommand)
login_manager.login_view = 'main.login'

#
# def make_Shell_context():
#     return dict(app=app,db=db,d=data)
# manager.add_command("Shell",Shell(make_context=make_Shell_context))
#
#

"""
    user commands
    on Saturday operations
"""

@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    print(user)
    return user  # 返回用户对象

if __name__ == '__main__':
    app.run()