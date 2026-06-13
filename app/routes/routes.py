import os
import json
import secrets
from flask import render_template, flash, redirect, url_for, request, session, abort
from flask_login import current_user, login_user, login_required, logout_user
from flask_mail import Message
from app.forms import (PostForm, RegistrationForm, LoginForm, UpdateAccountForm,
                       RequestResetForm, ResetPasswordForm)
from werkzeug.utils import secure_filename
from app.models import Post, User
from app import app, db, bcrypt, mail
from app.utilities import (load_estate_data, load_blog_data, featuring_data,
                           merge_estate_listings, post_to_listing, get_form_data,
                           perform_filtering, search_listings, index_listing)

exclusion_strings = ['101evler-cache/user_profile_crop/agent-profile/crop/', 'https://www.101evler.com/v4/images/abstract-user-1.svg',
                     '/101evler-cache/user-logo-svg/', 'www.101evler.com/v4/images/cancel_1.svg']


@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        msg = Message(subject, sender=email,
                      recipients=[app.config['ENQUIRY_RECIPIENT']])
        msg.body = message
        mail.send(msg)
        flash('Enquiry placed successfully', 'success')
        return "Sent"
    except Exception as e:
        flash(f'An error occurred while sending the email: {str(e)}', 'error')
        return "Error"


@app.route('/search', methods=['POST', 'GET'])
def search():

    query = request.values.get('query') or ''
    city, status, min_price, max_price, property_type = get_form_data()
    search_results = search_listings(query, city, status, min_price, max_price, property_type)
    return render_template('search_results.html', hits=search_results, query=query)


@app.route('/')
def home_page() -> str:
    blogs_ = load_blog_data()

    blogs = list()

    for blog in blogs_:
        if blog['Image Cover']:
            blogs.append(blog)

    return render_template('landing_page.html', blogs=blogs)


@app.route("/register", methods=['GET', 'POST'])
def register() -> str:
    '''Register a new user'''
    if current_user.is_authenticated:
        return redirect(url_for('properties'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Login route


@app.route("/login", methods=['GET', 'POST'])
def login():
    '''Login an existing user'''
    if current_user.is_authenticated:
        return redirect(url_for('properties'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('properties'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

# Add listing route


@app.route('/add-listing', methods=['POST', 'GET'])
@login_required
def add_listing():
    '''Add a new property listing'''
    form = PostForm()

    if "file_urls" not in session:
        session['file_urls'] = []
    file_urls = session['file_urls']

    if request.method == 'POST':
        try:
            for uploaded_file in request.files.getlist('file'):
                filename = secure_filename(uploaded_file.filename)
                if filename != '':
                    file_ext = os.path.splitext(filename)[1]
                    if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                        flash('Invalid Image', 'danger')
                        return redirect(url_for('add_listing'))
                    uploaded_file.save(os.path.join(
                        app.config['UPLOAD_PATH'], filename))
                    file_urls.append(url_for('static', filename=f'uploads/{filename}'))

            session['file_urls'] = file_urls

            if form.validate_on_submit():
                post = Post(file_path=json.dumps(file_urls),
                            title=form.title.data,
                            rent=form.rent.data,
                            location=form.location.data,
                            phone=form.phone.data, whatsapp=form.whatsapp.data, description=form.description.data,
                            bedrooms=form.bedrooms.data, bathrooms=form.bathrooms.data, area=form.area.data, author=current_user,
                            status=form.status.data,
                            furnishes=form.furnishes.data,
                            outside_features=form.outside_features.data)

                try:
                    db.session.add(post)
                    db.session.commit()
                    try:
                        index_listing(post_to_listing(post))
                    except Exception as index_error:
                        print(f'Listing saved but not indexed: {index_error}')
                    flash('Property Enlisted!', 'success')
                    session.pop('file_urls', None)
                    return redirect(url_for('properties'))
                except Exception as e:
                    db.session.rollback()
                    flash(
                        'An error occurred while enlisting the property. Please try again.', 'danger')
                    print(str(e))

        except Exception as e:
            flash(
                f'Error occurred while processing the request: {e}', 'danger')

    return render_template('add_listing.html', form=form)


@app.route('/properties', methods=['POST', 'GET'])
def properties():
    page = request.args.get('page', 1, type=int)
    items_per_page = 15

    estate_data = load_estate_data()

    posts = Post.query.order_by(Post.timestamp.desc()).all()
    posts_data = [post_to_listing(post) for post in posts]

    # Owner-direct listings surface first, ahead of the scraped inventory.
    json_data = posts_data + merge_estate_listings(estate_data)

    # Apply the filter form (city / status / price / type) when any field is set.
    city, status, min_price, max_price, property_type = get_form_data()
    if any([city, status, min_price, max_price, property_type]):
        json_data = perform_filtering(json_data, city, status, min_price, max_price, property_type)

    featured_data = featuring_data(estate_data["lefke_data"],
                                   estate_data["guzelyurt_data"],
                                   estate_data["featured_data"],
                                   estate_data["rent_data"],
                                   estate_data["iskele_data"],
                                   estate_data["magusa_data"],
                                   estate_data["konut_data"],
                                   estate_data["cyprus_data"])

    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(json_data))
    current_page_data = json_data[start_idx:end_idx]

    total_pages = len(json_data) // items_per_page

    return render_template('properties.html', current_page_data=current_page_data, featured_data=featured_data, page=page, total_pages=total_pages)


@app.route('/to-buy')
def to_buy():
    page = request.args.get('page', 1, type=int)
    for_sale = []
    items_per_page = 12

    json_data = [post_to_listing(p) for p in Post.query.order_by(Post.timestamp.desc())] + merge_estate_listings()

    for item in json_data:
        if item['Status'] == "For Sale":
            for_sale.append(item)

    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(for_sale))
    current_page_data = for_sale[start_idx:end_idx]

    return render_template('to_buy.html', current_page_data=current_page_data, page=page,
                           total_pages=len(for_sale)//items_per_page)


@app.route('/to-rent')
def to_rent():
    page = request.args.get('page', 1, type=int)
    items_per_page = 10
    for_rent = []
    json_data = [post_to_listing(p) for p in Post.query.order_by(Post.timestamp.desc())] + merge_estate_listings()

    for item in json_data:
        if item['Status'] == 'To Rent':
            for_rent.append(item)

    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(for_rent))
    current_page_data = for_rent[start_idx:end_idx]

    return render_template('to_rent.html', current_page_data=current_page_data, page=page, total_pages=len(for_rent)//items_per_page)


@app.route('/feature/<feature_name>')
def feature_detail(feature_name):

    json_data = merge_estate_listings()

    if feature_name == 'bus-stop':
        feature = 'Bus Stop'
        filtered_data = []

        for property_listing in json_data:
            for feature_dict in property_listing.get("Outside Features", []):
                for key, value in feature_dict.items():
                    if feature in key:
                        filtered_data.append(property_listing)

        return render_template('features.html', title=feature_name, filtered_data=filtered_data, )

    elif feature_name == 'swimming-pool':
        feature = 'Pool'
        filtered_data = [item for item in json_data if feature in item.get(
            "Pool", [])]
        return render_template('features.html', title=feature_name, filtered_data=filtered_data, )

    elif feature_name == 'private-security':
        feature = 'Security Cam'
        filtered_data = [item for item in json_data if feature in item.get(
            "Outside Features", [])]
        return render_template('features.html', title=feature_name, filtered_data=filtered_data, )

    elif feature_name == 'medical-center':
        feature = 'Hastanesi'
        filtered_data = []

        for property_listing in json_data:
            for feature_dict in property_listing.get("Outside Features", []):
                for key, value in feature_dict.items():
                    if feature in key:
                        filtered_data.append(property_listing)

        return render_template('features.html', title=feature_name, filtered_data=filtered_data)

    elif feature_name == 'building-age':
        feature = 'New Building'
        filtered_data = [item for item in json_data if feature in item.get(
            "Building Age", [])]
        return render_template('features.html', title=feature_name, filtered_data=filtered_data, )

    elif feature_name == 'furnished':
        feature = 'Furnished'
        filtered_data = [item for item in json_data if feature in item.get(
            'Furnishing Type', [])]
        return render_template('features.html', title=feature_name, filtered_data=filtered_data, )

    elif feature_name == 'park':
        feature = 'Closed Park'
        filtered_data = [item for item in json_data if feature in item.get(
            "Outside Features", [])]
        return render_template('features.html', title=feature_name, filtered_data=filtered_data, )

    elif feature_name == 'with-garden':
        feature = 'Yes'
        filtered_data = [item for item in json_data if feature in item.get(
            "Garden", [])]
        return render_template('features.html', title=feature_name, filtered_data=filtered_data, )

    else:
        return "Invalid feature name"


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout() -> str:
    '''Logout the current user'''
    logout_user()
    return redirect(url_for('home_page'))


def save_profile_picture(form_picture) -> str:
    '''Save an uploaded profile picture to static/profile_pics and return its
    filename. Resizes with Pillow when available, otherwise stores as-is.'''
    random_hex = secrets.token_hex(8)
    _, ext = os.path.splitext(secure_filename(form_picture.filename))
    picture_fn = f'{random_hex}{ext}'
    picture_dir = os.path.join(app.root_path, 'static', 'profile_pics')
    os.makedirs(picture_dir, exist_ok=True)
    picture_path = os.path.join(picture_dir, picture_fn)
    try:
        from PIL import Image
        image = Image.open(form_picture)
        image.thumbnail((150, 150))
        image.save(picture_path)
    except Exception:
        form_picture.seek(0)
        form_picture.save(picture_path)
    return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    '''View and edit the logged-in user's profile.'''
    form = UpdateAccountForm()
    if form.validate_on_submit():
        try:
            if form.picture.data:
                current_user.profile_image = save_profile_picture(form.picture.data)
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('account'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your account. Please try again.', 'danger')
            print(str(e))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename=f'profile_pics/{current_user.profile_image}')
    return render_template('account.html', form=form, image_file=image_file)


@app.route('/my-listings')
@login_required
def my_listings():
    '''List the current user's own property posts.'''
    posts = Post.query.filter_by(author=current_user).order_by(Post.timestamp.desc()).all()
    return render_template('my_listings.html', posts=posts)


@app.route('/listing/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_listing(post_id):
    '''Edit one of the current user's listings.'''
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        try:
            post.status = form.status.data
            post.title = form.title.data
            post.rent = form.rent.data
            post.location = form.location.data
            post.phone = form.phone.data
            post.whatsapp = form.whatsapp.data
            post.description = form.description.data
            post.bedrooms = form.bedrooms.data
            post.bathrooms = form.bathrooms.data
            post.area = form.area.data
            post.furnishes = form.furnishes.data
            post.outside_features = form.outside_features.data
            db.session.commit()
            flash('Your listing has been updated!', 'success')
            return redirect(url_for('my_listings'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the listing. Please try again.', 'danger')
            print(str(e))
    elif request.method == 'GET':
        form.status.data = post.status
        form.title.data = post.title
        form.rent.data = post.rent
        form.location.data = post.location
        form.phone.data = post.phone
        form.whatsapp.data = post.whatsapp
        form.description.data = post.description
        form.bedrooms.data = post.bedrooms
        form.bathrooms.data = post.bathrooms
        form.area.data = post.area
        form.furnishes.data = post.furnishes
        form.outside_features.data = post.outside_features
    return render_template('edit_listing.html', form=form, post=post)


@app.route('/listing/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_listing(post_id):
    '''Delete one of the current user's listings.'''
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    try:
        db.session.delete(post)
        db.session.commit()
        flash('Your listing has been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the listing. Please try again.', 'danger')
        print(str(e))
    return redirect(url_for('my_listings'))


def send_reset_email(user) -> None:
    '''Email a password-reset link to the user.'''
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=app.config['ENQUIRY_RECIPIENT'],
                  recipients=[user.email])
    reset_url = url_for('reset_token', token=token, _external=True)
    msg.body = (f'To reset your password, visit the following link:\n{reset_url}\n\n'
                'If you did not make this request, simply ignore this email.')
    mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    '''Request a password-reset email.'''
    if current_user.is_authenticated:
        return redirect(url_for('properties'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        try:
            send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Could not send the reset email. Please try again later.', 'danger')
            print(str(e))
    return render_template('reset_request.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    '''Reset the password using a valid token.'''
    if current_user.is_authenticated:
        return redirect(url_for('properties'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token.', 'success')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            db.session.commit()
            flash('Your password has been updated! You are now able to log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while resetting your password. Please try again.', 'danger')
            print(str(e))
    return render_template('reset_token.html', form=form)
