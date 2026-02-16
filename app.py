from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from game_logic import spin_round, apply_replacement

import random

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# -------------------------
# Database Model
# -------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    wins = db.Column(db.Integer, default=0)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -------------------------
# Wheel Logic
# -------------------------
def spin_wheel():
    return random.randint(10, 100)


# -------------------------
# Routes
# -------------------------
@app.route("/")
@login_required
def home():
    did_cheat = session.get("did_cheat", None)
    state = session.get("last_state")
    last_message = session.get("last_message")
    won_last_round = session.get("won_last_round", False)
    return render_template("home.html", did_cheat=did_cheat, state=state, last_message=last_message, won_last_round=won_last_round)





from flask import session  # add near the top if not already there

@app.route("/set_cheat", methods=["POST"])
def set_cheat():
    # expects "cheat" = "yes" or "no"
    cheat = request.form.get("cheat", "no").lower()
    session["did_cheat"] = (cheat == "yes")

    # reset any in-progress spin when changing this
    session.pop("last_state", None)
    session.pop("last_message", None)

    return redirect(url_for("home"))

@app.route("/spin", methods=["POST"])
@login_required
def spin():
    did_cheat = session.get("did_cheat", None)
    if did_cheat is None:
        return redirect(url_for("home"))

    # Winner's Wheel bonus if they won the previous round
    did_win_last_round = session.get("won_last_round", False)

    state = spin_round(did_cheat=did_cheat, did_win=did_win_last_round)

    # Consume it so Winner's Wheel only applies once
    session["won_last_round"] = False

    session["last_state"] = state
    session["last_message"] = None
    return redirect(url_for("home"))


@app.route("/replace", methods=["POST"])
@login_required
def replace():
    state = session.get("last_state")
    if not state:
        return redirect(url_for("home"))

    wheel_to_replace = request.form.get("wheel")
    state, msg = apply_replacement(state, wheel_to_replace)

    session["last_state"] = state
    session["last_message"] = msg
    return redirect(url_for("home"))

@app.route("/win", methods=["POST"])
@login_required
def win():
    if session.get("last_state"):
        current_user.wins += 1
        db.session.commit()
        session["won_last_round"] = True

    # clear round + force re-pick cheat next round
    session.pop("last_state", None)
    session.pop("last_message", None)
    session.pop("did_cheat", None)

    return redirect(url_for("home"))



@app.route("/clear_spin", methods=["POST"])
@login_required
def clear_spin():
    session["won_last_round"] = False

    # clear round + force re-pick cheat next round
    session.pop("last_state", None)
    session.pop("last_message", None)
    session.pop("did_cheat", None)

    return redirect(url_for("home"))



@app.route("/leaderboard")
@login_required
def leaderboard():
    users = User.query.order_by(User.wins.desc()).all()
    return render_template("leaderboard.html", users=users)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        hashed_pw = generate_password_hash(request.form["password"])
        user = User(username=request.form["username"], password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
