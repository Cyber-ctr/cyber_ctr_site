import os
from datetime import datetime

from flask import Flask, flash, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, CSRFProtect
from flask_talisman import Talisman
from wtforms import EmailField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length

db = SQLAlchemy()
csrf = CSRFProtect()

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), nullable=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class ContactForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=80)])
    email = EmailField("Email address", validators=[DataRequired(), Email(), Length(max=120)])
    company = StringField("Company / Project", validators=[Length(max=120)])
    message = TextAreaField("Project brief", validators=[DataRequired(), Length(min=20, max=2000)])
    submit = SubmitField("Send message")

def _database_uri():
    uri = os.getenv("DATABASE_URL", "sqlite:///cyber_ctr.db")
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    return uri

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-change-this-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = _database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["WTF_CSRF_TIME_LIMIT"] = None
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

    db.init_app(app)
    csrf.init_app(app)

    Talisman(
        app,
        force_https=bool(os.getenv("FLASK_ENV", "").lower() != "development"),
        content_security_policy={
            "default-src": "'self'",
            "style-src": ["'self'"],
            "script-src": ["'self'"],
            "img-src": ["'self'", "data:"],
            "font-src": ["'self'"],
            "base-uri": "'self'",
            "form-action": "'self'",
        },
    )

    with app.app_context():
        db.create_all()

    @app.route("/", methods=["GET", "POST"])
    def index():
        form = ContactForm()
        if form.validate_on_submit():
            db.session.add(ContactMessage(
                name=form.name.data.strip(),
                email=form.email.data.strip().lower(),
                company=(form.company.data or "").strip() or None,
                message=form.message.data.strip(),
            ))
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
        return render_template("index.html", form=form, stats=stats, services=services, process=process, stack=stack, showcases=showcases, current_year=datetime.utcnow().year)

    @app.route("/thank-you")
    def thank_you():
        return render_template("thanks.html", current_year=datetime.utcnow().year)

    @app.route("/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(404)
    def not_found(_):
        return render_template("404.html", current_year=datetime.utcnow().year), 404

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
