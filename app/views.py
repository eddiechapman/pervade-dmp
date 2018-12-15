from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from datetime import datetime
from app.forms import LoginForm, RegistrationForm, CodingForm, ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_password_reset_email
from app.models import Award, User, Title, Abstract, Project


@app.before_request
def session_management():
    """Initialize Flask session storage to remember skipped awards."""
    session.permanent = True
    if 'skipped_awards' not in session:
        session['skipped_awards'] = []


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

# TODO: Move coding stuff to separate directory
@app.route('/get_award')
@login_required
def get_award():
    """Retrieve a single award that has not been coded or skipped."""
    award = Award.query.filter(
        # No timestamp (added when coding form is submitted)
        Award.timestamp == None,
        # No skipped awards matching current award ID
        ~Award.id.in_(session['skipped_awards'])
    # 404 error page is returned if no results
    ).first_or_404()
    return redirect(url_for('code_award', award_id=award.id))


# TODO: Move coding stuff to separate directory
@app.route('/skip_award/<int:award_id>')
@login_required
def skip_award(award_id):
    """Add current award ID to list of skipped awards."""
    session['skipped_awards'].append(award_id)
    return redirect(url_for('get_award'))


# TODO: Move coding stuff to separate directory
@app.route('/code_award/<int:award_id>', methods=['GET', 'POST'])
@login_required
def code_award(award_id):
    """Display award data and coding form. Process form submission."""
    award = Award.query.get(award_id)
    form = CodingForm()
    # TODO: probably can't use validate_on_submit anymore...
    if form.validate_on_submit():
        Title(
                project         = None,
                user            = current_user,
                timestamp       = datetime.utcnow(),
                pervasive_data  = form.title_pervasive_data.data,
                data_sci        = form.title_data_science.data,
                big_data        = form.title_big_data.data,
                case_study      = form.title_case_study.data,
                data_synonyms   = form.title_data_synonyms.data
                )
        Abstract(
                project         = None,
                user            = current_user,
                timestamp       = datetime.utcnow(),
                pervasive_data  = form.abstract_pervasive_data.data,
                data_sci        = form.abstract_data_science.data,
                big_data        = form.abstract_big_data.data,
                case_study      = form.abstract_case_study.data,
                data_synonyms   = form.abstract_data_synonyms.data
                )
        db.session.commit()
        flash('Coding data submitted.')
        return redirect(url_for('get_award'))
    return render_template('coding.html', award=award, form=form)


# TODO: Move user stuff to a separate directory
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate login credentials, retrieve user info from database."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


# TODO: Move user stuff to a separate directory
@app.route('/logout')
def logout():
    """Log user out and clear session of skipped awards."""
    session.clear()
    logout_user()
    return redirect(url_for('index'))


# TODO: Move user stuff to a separate directory
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Add user to the database."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# TODO: Move user stuff to a separate directory
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

# TODO: Move user stuff to a separate directory
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)