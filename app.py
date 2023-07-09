from hack import app, create_db, db
from flask import render_template, redirect, abort, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from hack.forms import LoginForm, RegForm, SearchForm
from hack.models import User, Product, UserProduct
from werkzeug.security import generate_password_hash, check_password_hash
import uuid as uuid
import stripe
from sqlalchemy import or_


stripe.api_key = app.config['STRIPE_SECRET_KEY']

create_db(app)


@app.route('/')
def home():
    searchform = SearchForm()
    return render_template('index.html', searchform=searchform)

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    searchform = SearchForm()
    form = RegForm()
    mess=''
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            mess = 'Account already exists'
        else:
            new_user = User(username=username, email=email, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            if current_user.is_authenticated:
                return redirect('admin')
            else:
                login_user(new_user)
                return redirect(url_for('home'))
    if current_user.is_authenticated and current_user.username != 'XINO':
        return abort(404)
    return render_template('reg.html', searchform=searchform, form=form, mess=mess)

@app.route('/login', methods=['GET', 'POST'])
def login():
    searchform = SearchForm()
    form = LoginForm()
    mess=''
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            mess = 'Email not found'
        else:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('home'))
            else:
                mess = 'Incorrect password'
    if current_user.is_authenticated and current_user.username != 'XINO':
        return abort(404)
    return render_template('login.html', searchform=searchform, mess=mess, form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(request.referrer)

@app.route('/explore')
def explore():
    searchform = SearchForm()
    products = Product.query.all()
    return render_template('explore.html', searchform=searchform, products=products)

@app.route('/addtocart/<id>')
@login_required
def addtocart(id):
    product = Product.query.filter_by(id=id).first()
    if product:
        user_product = UserProduct(product_id=product.id, user_id=current_user.id)
        current_user.products.append(user_product)
        db.session.add(current_user)
        db.session.add(product)
        db.session.add(user_product)
        db.session.commit()
        flash('Product added to cart successfully.')
    return redirect(request.referrer)

@app.route('/products/<id>')
def product(id):
    searchform = SearchForm()
    product = Product.query.filter_by(id=id).first()
    prods = Product.query.all()
    prods.remove(product)
    return render_template('product.html', searchform=searchform, prod=product, prods=prods)

@app.route('/increase_qty/<user_id>/<prod_id>')
@login_required
def increase_qty(user_id, prod_id):
    prod = UserProduct.query.filter_by(user_id=user_id, product_id=prod_id).first()
    if prod.qty != 0:
        prod.qty += 1
    db.session.add(prod)
    db.session.commit()
    return redirect(request.referrer)

@app.route('/sendsearch', methods=['GET', 'POST'])
def send_search():
    form = SearchForm()
    if form.validate_on_submit():
        print(form.query.data)
        return redirect(url_for('return_search', q=form.query.data))
    return redirect(request.referrer)

@app.route('/search')
def return_search():
    searchform = SearchForm()
    query = request.args.get('q')
    results = Product.query.filter(Product.name.like('%' + query + '%')).all()
    return render_template('results.html', searchform=searchform, results=results)

@app.route('/cart')
@login_required
def cart():
    searchform = SearchForm()
    total = 0
    user_products = UserProduct.query.filter_by(user_id=current_user.id).all()

    products = (
        db.session.query(Product)
        .join(UserProduct)
        .filter(UserProduct.user_id == current_user.id)
        .all()
    )

    for entry in current_user.products:
        product = Product.query.filter_by(id=entry.product_id).first()
        total += product.price * entry.qty
    key=app.config['STRIPE_PUBLISHABLE_KEY']
    return render_template('cart.html', searchform=searchform, total=total, key=key, products=products, user_products=user_products)

@app.route('/decrease_qty/<user_id>/<prod_id>')
@login_required
def decrease_qty(user_id, prod_id):
    prod = UserProduct.query.filter_by(user_id=user_id, product_id=prod_id).first()
    if prod.qty == 1:
        current_user.products.remove(prod)
        db.session.delete(prod)
        db.session.commit()
    if prod.qty > 1:
        prod.qty -= 1
        db.session.add(prod)
        db.session.commit()
    return redirect(request.referrer)

@app.route('/thankyou', methods=['GET', 'POST'])
@login_required
def thank_you():
    searchform = SearchForm()
    for i in current_user.products:
        current_user.products.remove(i)
        db.session.delete(i)
        db.session.commit()
    return render_template('thankyou.html', searchform=searchform)


if __name__ == '__main__':
    app.run(debug=True)
