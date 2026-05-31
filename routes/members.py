from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Member

members_bp = Blueprint('members', __name__)

@members_bp.route('/')
def list_members():
    members = Member.query.all()
    return render_template('members/list.html', members=members)

@members_bp.route('/add', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        member = Member(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form.get('phone'),
            address=request.form.get('address')
        )
        db.session.add(member)
        db.session.commit()
        flash('Member added successfully.', 'success')
        return redirect(url_for('members.list_members'))
    return render_template('members/add.html')

@members_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_member(id):
    member = Member.query.get_or_404(id)
    if request.method == 'POST':
        member.name = request.form['name']
        member.email = request.form['email']
        member.phone = request.form.get('phone')
        member.address = request.form.get('address')
        db.session.commit()
        flash('Member updated.', 'success')
        return redirect(url_for('members.list_members'))
    return render_template('members/add.html', member=member)