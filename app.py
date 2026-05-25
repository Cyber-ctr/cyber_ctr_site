import os
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from flask_wtf import CSRFProtect, FlaskForm
from werkzeug.security import check_password_hash
from wtforms import EmailField, PasswordField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), nullable=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class AdminUser(UserMixin):
    def __init__(self, user_id: str):
        self.id = user_id


class ContactForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=80)])
    email = EmailField("Email address", validators=[DataRequired(), Email(), Length(max=120)])
    company = StringField("Company / Project", validators=[Length(max=120)])
    message = TextAreaField("Project brief", validators=[DataRequired(), Length(min=20, max=2000)])
    submit = SubmitField("Send message")


class AdminLoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField("Sign in")


class EmptyForm(FlaskForm):
    pass


def _database_uri():
    uri = os.getenv("DATABASE_URL", "sqlite:///cyber_ctr_v2.db")
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    return uri


def _admin_username():
    return os.getenv("ADMIN_USERNAME", "admin")


def _admin_password_matches(password: str) -> bool:
    pw_hash = os.getenv("ADMIN_PASSWORD_HASH", "").strip()
    if pw_hash:
        return check_password_hash(pw_hash, password)
    return password == os.getenv("ADMIN_PASSWORD", "CyberCtr@2026Secure")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "Thisisamatterofsecrecy!!")
    app.config["SQLALCHEMY_DATABASE_URI"] = _database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["WTF_CSRF_TIME_LIMIT"] = None
    app.config["WTF_CSRF_SSL_STRICT"] = False
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

    db.init_app(app)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "admin_login"
    login_manager.login_message_category = "info"

    Talisman(
        app,
        force_https=bool(os.getenv("FLASK_ENV", "").lower() != "development"),
        content_security_policy={
            "default-src": ["'self'"],
            "style-src": ["'self'"],
            "script-src": ["'self'"],
            "img-src": ["'self'", "data:"],
            "font-src": ["'self'"],
            "base-uri": ["'self'"],
            "form-action": ["'self'"],
            "frame-ancestors": ["'none'"],
        },
    )

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        if user_id == "admin":
            return AdminUser("admin")
        return None

    @app.route("/", methods=["GET", "POST"])
    def index():
        form = ContactForm()

        if form.validate_on_submit():
            db.session.add(
                ContactMessage(
                    name=form.name.data.strip(),
                    email=form.email.data.strip().lower(),
                    company=(form.company.data or "").strip() or None,
                    message=form.message.data.strip(),
                )
            )
            db.session.commit()
            flash("Thanks. Your message has been received. Cyber-ctr will get back to you soon.", "success")
            return redirect(url_for("thank_you"))

        stats = {"projects": 18, "response_time": "< 24h", "focus": "Security-first", "delivery": "Remote"}
        services = [
            {"title": "Web Application Development", "desc": "Modern Flask-based web applications built for speed, clarity, and scale."},
            {"title": "Responsive Digital Solutions", "desc": "Clean interfaces that perform beautifully across mobile, tablet, and desktop."},
            {"title": "Secure Backend Systems", "desc": "Robust data workflows, strong validation, and database-driven reliability."},
            {"title": "Startup Product Strategy", "desc": "Practical technical direction for early-stage teams that need to move fast."},
        ]
        process = [
            ("Discover", "We define the problem, scope the solution, and align on business goals."),
            ("Design", "We shape a premium interface and an intuitive user journey."),
            ("Build", "We implement the application with secure, maintainable code."),
            ("Launch", "We deploy, refine, and support your product as it grows."),
        ]
        stack = ["Flask", "PostgreSQL", "JavaScript", "HTML5", "CSS3", "Gunicorn", "Render", "GitHub"]
        showcases = [
            ("Secure Landing Pages", "High-conversion startup pages with premium visual polish."),
            ("Business Portals", "Structured systems that organize clients, data, and workflows."),
            ("Admin Dashboards", "Clear operational views for teams that need control and insight."),
        ]

        return render_template(
            "index.html",
            form=form,
            stats=stats,
            services=services,
            process=process,
            stack=stack,
            showcases=showcases,
            current_year=datetime.utcnow().year,
        )

    @app.route("/thank-you")
    def thank_you():
        return render_template("thanks.html", current_year=datetime.utcnow().year)

    @app.route("/health")
    def health():
        return {"status": "ok"}

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        form = AdminLoginForm()

        if form.validate_on_submit():
            if form.username.data.strip() == _admin_username() and _admin_password_matches(form.password.data):
                login_user(AdminUser("admin"))
                flash("Welcome back, admin.", "success")
                return redirect(url_for("admin_dashboard"))

            flash("Invalid admin credentials.", "error")

        return render_template("admin_login.html", form=form, current_year=datetime.utcnow().year)

    @app.route("/admin/logout", methods=["POST"])
    @login_required
    def admin_logout():
        logout_user()
        flash("You have been logged out.", "success")
        return redirect(url_for("index"))

    @app.route("/admin")
    @login_required
    def admin_redirect():
        return redirect(url_for("admin_dashboard"))

    @app.route("/admin/dashboard")
    @login_required
    def admin_dashboard():
        total_messages = ContactMessage.query.count()
        unread_messages = ContactMessage.query.filter_by(is_read=False).count()
        recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
        action_form = EmptyForm()

        return render_template(
            "admin_dashboard.html",
            total_messages=total_messages,
            unread_messages=unread_messages,
            recent_messages=recent_messages,
            action_form=action_form,
            current_year=datetime.utcnow().year,
        )

    @app.route("/admin/messages")
    @login_required
    def admin_messages():
        messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
        action_form = EmptyForm()
        return render_template(
            "admin_messages.html",
            messages=messages,
            action_form=action_form,
            current_year=datetime.utcnow().year,
        )

    @app.route("/admin/messages/<int:message_id>/read", methods=["POST"])
    @login_required
    def admin_mark_read(message_id):
        message = ContactMessage.query.get_or_404(message_id)
        message.is_read = True
        db.session.commit()
        flash("Message marked as read.", "success")
        return redirect(request.referrer or url_for("admin_messages"))

    @app.route("/admin/messages/<int:message_id>/delete", methods=["POST"])
    @login_required
    def admin_delete_message(message_id):
        message = ContactMessage.query.get_or_404(message_id)
        db.session.delete(message)
        db.session.commit()
        flash("Message deleted.", "success")
        return redirect(request.referrer or url_for("admin_messages"))

    @app.errorhandler(404)
    def not_found(_):
        return render_template("404.html", current_year=datetime.utcnow().year), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
