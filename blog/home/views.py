# coding=utf-8
from flask import g, render_template
from .blueprint import blueprint
#from .models import User

@blueprint.route("/")
def index():
	#g.db_session.add(User('jack'))
	#g.db_session.commit()
	navigation = [
			{"caption": u"首页", "href": "#"},
			{"caption": u"关于中宇", "href": "#"},
			{"caption": u"新闻中心", "href": "#"},
			{"caption": u"品牌", "href": "#"},
			{"caption": u"浴室空间", "href": "#"},
			{"caption": u"产品展示", "href": "#"},
			{"caption": u"销售专区", "href": "#"},
	]
	return render_template('index.html', navigation=navigation)
