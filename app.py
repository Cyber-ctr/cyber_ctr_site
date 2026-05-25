import os
from datetime import datetime

from flask import Flask, flash, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, CSRFProtect
from flask_talisman import Talisman
from flask_mail import Mail, Message

from wtforms import EmailField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length

# ---------------------------------------------------
# INITIALIZATION
# ---------------------------------------------------

db = SQLAlchemy()
csrf = CSRFProtect()
mail = Mail()

# ---------------------------------------------------
# DATABASE MODEL
# ---------------------------------------------------


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(80), nullable=False)

    email = db.Column(db.String(120), nullable=False)

    company = db.Column(db.String(120), nullable=True)

    message = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

# ---------------------------------------------------
# CONTACT FORM
# ---------------------------------------------------

class ContactForm(FlaskForm):

    name = StringField(
        "Full name",
        validators=[
            DataRequired(),
            Length(min=2, max=80)
        ]
    )

    email = EmailField(
        "Email address",
        validators=[
            DataRequired(),
            Email(),
            Length(max=120)
        ]
    )

    company = StringField(
        "Company / Project",
        validators=[
            Length(max=120)
        ]
    )

    message = TextAreaField(
        "Project brief",
        validators=[
            DataRequired(),
            Length(min=20, max=2000)
        ]
    )

    submit = SubmitField("Send message")

# ---------------------------------------------------
# DATABASE URI
# ---------------------------------------------------

def _database_uri():

    uri = os.getenv(
        "DATABASE_URL",
        "sqlite:///cyber_ctr.db"
    )

    if uri.startswith("postgres://"):
        uri = uri.replace(
            "postgres://",
            "postgresql://",
            1
        )

    return uri

# ---------------------------------------------------
# CREATE APP
# ---------------------------------------------------

def create_app():

    app = Flask(__name__)

    # ---------------------------------------------------
    # SECURITY CONFIG
    # ---------------------------------------------------

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "dev-change-this-secret"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = _database_uri()

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["WTF_CSRF_TIME_LIMIT"] = None

    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

    # ---------------------------------------------------
    # EMAIL CONFIGURATION
    # ---------------------------------------------------

    app.config["MAIL_SERVER"] = "smtp.gmail.com"

    app.config["MAIL_PORT"] = 587

    app.config["MAIL_USE_TLS"] = True

    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")

    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

    app.config["MAIL_DEFAULT_SENDER"] = os.getenv(
        "MAIL_USERNAME"
    )

    # ---------------------------------------------------
    # INITIALIZE EXTENSIONS
    # ---------------------------------------------------

    db.init_app(app)

    csrf.init_app(app)

    mail.init_app(app)

    # ---------------------------------------------------
    # SECURITY HEADERS
    # ---------------------------------------------------

    Talisman(
        app,

        force_https=bool(
            os.getenv(
                "FLASK_ENV",
                ""
            ).lower() != "development"
        ),

        content_security_policy={
            "default-src": "'self'",
            "style-src": [
                "'self'",
                "'unsafe-inline'"
            ],
            "script-src": [
                "'self'",
                "'unsafe-inline'"
            ],
            "img-src": [
                "'self'",
                "data:"
            ],
            "font-src": [
                "'self'"
            ],
            "base-uri": "'self'",
            "form-action": "'self'",
        },
    )

    # ---------------------------------------------------
    # CREATE DATABASE TABLES
    # ---------------------------------------------------

    with app.app_context():
        db.create_all()

    # ---------------------------------------------------
    # HOME ROUTE
    # ---------------------------------------------------

    @app.route("/", methods=["GET", "POST"])
    def index():

        form = ContactForm()

        if form.validate_on_submit():

            # ---------------------------------------------------
            # SAVE TO DATABASE
            # ---------------------------------------------------

            new_message = ContactMessage(
                name=form.name.data.strip(),

                email=form.email.data.strip().lower(),

                company=(
                    (form.company.data or "").strip() or None
                ),

                message=form.message.data.strip(),
            )

            db.session.add(new_message)

            db.session.commit()

            # ---------------------------------------------------
            # SEND EMAIL
            # ---------------------------------------------------

            try:

                msg = Message(
                    subject="New Cyber-ctr Contact Form Submission",

                    sender=app.config["MAIL_USERNAME"],

                    recipients=[
                        "thresholdtechnologylimited@gmail.com"
                    ]
                )

                msg.body = f"""
New Contact Form Submission

----------------------------------------

Name:
{form.name.data}

Email:
{form.email.data}

Company / Project:
{form.company.data or "N/A"}

----------------------------------------

Message:

{form.message.data}

----------------------------------------

Submitted At:
{datetime.utcnow()}
"""

                mail.send(msg)

                print("EMAIL SENT SUCCESSFULLY")

            except Exception as e:

                app.logger.exception(
                    f"EMAIL SENDING FAILED: {e}"
                )

            # ---------------------------------------------------
            # SUCCESS MESSAGE
            # ---------------------------------------------------

            flash(
                "Thanks. Your message has been received. Cyber-ctr will get back to you soon.",
                "success"
            )

            return redirect(url_for("thank_you"))

        # ---------------------------------------------------
        # WEBSITE CONTENT
        # ---------------------------------------------------

        stats = {
            "projects": 18,
            "response_time": "< 24h",
            "focus": "Security-first",
            "delivery": "Remote"
        }

        services = [
            {
                "title": "Web Application Development",
                "desc": "Modern Flask-based web applications built for speed, clarity, and scale."
            },

            {
                "title": "Responsive Digital Solutions",
                "desc": "Clean interfaces that perform beautifully across mobile, tablet, and desktop."
            },

            {
                "title": "Secure Backend Systems",
                "desc": "Robust data workflows, strong validation, and database-driven reliability."
            },

            {
                "title": "Startup Product Strategy",
                "desc": "Practical technical direction for early-stage teams that need to move fast."
            },
        ]

        process = [
            (
                "Discover",
                "We define the problem, scope the solution, and align on business goals."
            ),

            (
                "Design",
                "We shape a premium interface and an intuitive user journey."
            ),

            (
                "Build",
                "We implement the application with secure, maintainable code."
            ),

            (
                "Launch",
                "We deploy, refine, and support your product as it grows."
            ),
        ]

        stack = [
            "Flask",
            "PostgreSQL",
            "JavaScript",
            "HTML5",
            "CSS3",
            "Gunicorn",
            "Render",
            "GitHub"
        ]

        showcases = [
            (
                "Secure Landing Pages",
                "High-conversion startup pages with premium visual polish."
            ),

            (
                "Business Portals",
                "Structured systems that organize clients, data, and workflows."
            ),

            (
                "Admin Dashboards",
                "Clear operational views for teams that need control and insight."
            ),
        ]

        return render_template(
            "index.html",

            form=form,

            stats=stats,

            services=services,

            process=process,

            stack=stack,

            showcases=showcases,

            current_year=datetime.utcnow().year
        )

    # ---------------------------------------------------
    # THANK YOU PAGE
    # ---------------------------------------------------

    @app.route("/thank-you")
    def thank_you():

        return render_template(
            "thanks.html",
            current_year=datetime.utcnow().year
        )

    # ---------------------------------------------------
    # HEALTH CHECK
    # ---------------------------------------------------

    @app.route("/health")
    def health():

        return {"status": "ok"}

    # ---------------------------------------------------
    # 404 PAGE
    # ---------------------------------------------------

    @app.errorhandler(404)
    def not_found(_):

        return render_template(
            "404.html",
            current_year=datetime.utcnow().year
        ), 404

    return app

# ---------------------------------------------------
# APP ENTRY
# ---------------------------------------------------

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)