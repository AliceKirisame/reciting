import random, re

from flask import render_template, request, flash, redirect, url_for, abort, make_response
from flask.ext.login import login_required

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField

from .. import db
from ..models import InputWord

from . import exam
from .forms import WordForm, RespForm


@exam.route('/')
def index():
    group = db.session.query(InputWord.group).group_by(InputWord.group).all()

    length = len(group)

    if(length == 0):
        return redirect(url_for('exam.newWord'))

    return render_template('exam/exam.html', length=length)


@exam.route('/newWord', methods=['GET', 'POST'])
def newWord():
    form = WordForm()

    if form.validate_on_submit():
        new = InputWord(word=form.word.data, group=int(form.group.data), meaning=form.meaning.data)

        db.session.add(new)
        db.session.commit()

        flash('添加成功')

        return redirect(url_for('exam.newWord'))

    return render_template('exam/newword.html', form=form)


@exam.route('/<id>', methods=['GET', 'POST'])
def examIt(id):
    pawd = {1: '2120', 2: '2201', 3: '1011', 4: '2100', 5: '1200', 6: '0101'}

    try:
        id = int(id)
    except:
        abort(404)

    li = InputWord.query.filter_by(group=id).all()

    length = len(li)

    if(length < 10):
        abort(404)

    lsl = list(range(length))
    random.shuffle(lsl)
    print(lsl)

    class DynamicForm(Form):
        submit = SubmitField('submit')

    ls = ''
    for i in range(length):
        setattr(DynamicForm, 'word' + str(i+1), StringField(li[lsl[i]].meaning))
        ls += (str(lsl[i]) + ' ')

    form = DynamicForm()

    score = 0
    en = 0
    el = []

    if(form.validate_on_submit()):
        ls = request.cookies.get('ls')
        
        ns = '[0-9][0-9]*'

        lsl = re.findall(ns, ls)
        print(lsl)
        for i in range(length):

            if(getattr(form, 'word' + str(i+1)).data == li[int(lsl[i])].word):
                score += 1

            else:
                en += 1
                el.append(getattr(form, 'word' + str(i+1)).data)

        return render_template('exam/errorwords.html', en=en, el=el, pawd=pawd, id=id)

    resp = make_response(render_template('exam/exampage.html', li=li, length=length, form=form))

    resp.set_cookie('ls', ls, max_age=24*60*60)

    return resp