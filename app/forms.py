from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from .models import User

# Registration Form
class RegistrationForm(FlaskForm):
    """
    Form for user registration.

    Attributes:
        username (StringField): User's username.
        email (StringField): User's email address.
        password (PasswordField): User's password.
        submit (SubmitField): Submit button.

    Methods:
        validate_username(self, username): Validate username.
        validate_email(self, email): Validate email.
    """
    username = StringField('User Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """
        Validate username.

        Parameters:
            username (String): User's username.

        Raises:
            ValidationError: If username is already taken.
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        """
        Validate email.

        Parameters:
            email (String): User's email address.

        Raises:
            ValidationError: If email is already taken.
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

# Login Form
class LoginForm(FlaskForm):
    """
    Form for user login.

    Attributes:
        email (StringField): User's email address.
        password (PasswordField): User's password.
        remember (BooleanField): "Remember me" checkbox.
        submit (SubmitField): Submit button.
    """
    email = StringField('Email ', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me ')
    submit = SubmitField('Log In ')

# Update Account Form
class UpdateAccountForm(FlaskForm):
    """
    Form for updating user account details.

    Attributes:
        username (StringField): User's username.
        email (StringField): User's email address.
        picture (FileField): User's profile picture.
        submit (SubmitField): Submit button.

    Methods:
        validate_username(self, username): Validate username.
        validate_email(self, email): Validate email.
    """
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        """
        Validate username.

        Parameters:
            username (String): User's username.

        Raises:
            ValidationError: If username is already taken.
        """
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        """
        Validate email.

        Parameters:
            email (String): User's email address.

        Raises:
            ValidationError: If email is already taken.
        """
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class PostForm(FlaskForm):
    furnishes = StringField('Furnished', validators=[DataRequired()])
    file_path = FileField('file')
    title = StringField('Property Type', validators=[DataRequired(), Length(min=5, max=140)])
    whatsapp = StringField('Whatsapp',
                           validators=[DataRequired(), Length(min=10, max=14)],
                           render_kw={"Placeholder": "0533 ___ ____"})
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=14)],
                        render_kw={"Placeholder": "0533 ___ ____"})
    location = StringField('Address', validators=[DataRequired(), Length(min=5, max=140)],
                           render_kw={"Placeholder": "1 Bozkurt Sokak"})
    rent = StringField('Rent', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    bedrooms = StringField('Bedrooms', validators=[DataRequired()])
    bathrooms = StringField('Bathrooms', validators=[DataRequired()])
    outside_features = TextAreaField('Outside Features')
    area = StringField('Square Feet', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Request Password Reset Form
class RequestResetForm(FlaskForm):
    """
    Form for requesting a password reset.

    Attributes:
        email (StringField): User's email address.
        submit (SubmitField): Submit button.

    Methods:
        validate_email(self, email): Validate email.
    """
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request')

    def validate_email(self, email):
        """
        Validate email.

        Parameters:
            email (String): User's email address.

        Raises:
            ValidationError: If there is no account with the provided email.
        """
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

# Reset Password Form
class ResetPasswordForm(FlaskForm):
    """
    Form for resetting the password.

    Attributes:
        password (PasswordField): New password.
        confirm_password (PasswordField): Confirm new password.
        submit (SubmitField): Submit button.
    """
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


    