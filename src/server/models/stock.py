from server.extensions import db


class Users_Stocks(db.Model):
    __tablename__ = "users_stocks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    symbol = db.Column(db.String(4), unique=True, nullable=False)
    quantity = db.Column(db.Integer, unique=False, nullable=False)
