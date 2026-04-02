from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
from functools import wraps
from collections import defaultdict
from urllib.parse import quote_plus   # Important for special characters in password

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-for-assignment-2026'

# ====================== MYSQL CONFIGURATION ======================
MYSQL_HOST = '127.0.0.1'          # Best for Windows local MySQL
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Pass@123'       # Your password
MYSQL_DB = 'finance_dashboard'

# Properly encode password (handles @ symbol safely)
encoded_password = quote_plus(MYSQL_PASSWORD)

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{MYSQL_USER}:{encoded_password}@{MYSQL_HOST}/{MYSQL_DB}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ========================= MODELS =========================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='viewer')
    is_active = db.Column(db.Boolean, default=True)

    def get_id(self):
        return str(self.id)

class FinancialRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

# ========================= LOGIN MANAGER =========================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ========================= ROLE DECORATOR =========================
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role not in allowed_roles:
                flash('Access denied. Insufficient permissions.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ========================= ROUTES =========================
# (All your routes are kept exactly the same as the working SQLite version)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password) and user.is_active:
            login_user(user)
            flash(f'Welcome back, {user.username}! Role: {user.role}', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    records = FinancialRecord.query.all()
    total_income = sum(r.amount for r in records if r.type == 'income')
    total_expense = sum(r.amount for r in records if r.type == 'expense')
    net_balance = total_income - total_expense

    cat_income = defaultdict(float)
    cat_expense = defaultdict(float)
    for r in records:
        if r.type == 'income':
            cat_income[r.category] += r.amount
        else:
            cat_expense[r.category] += r.amount

    recent = sorted(records, key=lambda x: x.date, reverse=True)[:5]

    return render_template('dashboard.html',
                           total_income=total_income,
                           total_expense=total_expense,
                           net_balance=net_balance,
                           cat_income=cat_income,
                           cat_expense=cat_expense,
                           recent=recent)

@app.route('/records')
@login_required
@role_required(['analyst', 'admin'])
def records():
    type_filter = request.args.get('type')
    category_filter = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = FinancialRecord.query
    if type_filter: query = query.filter_by(type=type_filter)
    if category_filter: query = query.filter_by(category=category_filter)
    if start_date:
        query = query.filter(FinancialRecord.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(FinancialRecord.date <= datetime.strptime(end_date, '%Y-%m-%d').date())

    records_list = query.order_by(FinancialRecord.date.desc()).all()
    categories = [c[0] for c in db.session.query(FinancialRecord.category).distinct().all()]

    return render_template('records.html',
                           records=records_list,
                           categories=categories,
                           type_filter=type_filter,
                           category_filter=category_filter,
                           start_date=start_date,
                           end_date=end_date)

@app.route('/records/create', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def create_record():
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            if amount <= 0:
                raise ValueError("Amount must be positive")
            record = FinancialRecord(
                amount=amount,
                type=request.form['type'],
                category=request.form['category'],
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                notes=request.form.get('notes', ''),
                created_by=current_user.id
            )
            db.session.add(record)
            db.session.commit()
            flash('Record created successfully!', 'success')
            return redirect(url_for('records'))
        except Exception as e:
            flash(f'Invalid data: {str(e)}', 'danger')
    return render_template('create_record.html')

@app.route('/records/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def edit_record(record_id):
    record = FinancialRecord.query.get_or_404(record_id)
    if request.method == 'POST':
        try:
            record.amount = float(request.form['amount'])
            record.type = request.form['type']
            record.category = request.form['category']
            record.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            record.notes = request.form.get('notes', '')
            db.session.commit()
            flash('Record updated successfully!', 'success')
            return redirect(url_for('records'))
        except Exception as e:
            flash(f'Invalid data: {str(e)}', 'danger')
    return render_template('edit_record.html', record=record)

@app.route('/records/delete/<int:record_id>')
@login_required
@role_required(['admin'])
def delete_record(record_id):
    record = FinancialRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    flash('Record deleted successfully!', 'success')
    return redirect(url_for('records'))

@app.route('/users')
@login_required
@role_required(['admin'])
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

# ========================= SEED DATA =========================
def create_tables_and_seed():
    try:
        with app.app_context():
            db.create_all()
            if User.query.count() == 0:
                admin = User(username='admin', password_hash=generate_password_hash('admin123'), role='admin')
                analyst = User(username='analyst', password_hash=generate_password_hash('analyst123'), role='analyst')
                viewer = User(username='viewer', password_hash=generate_password_hash('viewer123'), role='viewer')
                db.session.add_all([admin, analyst, viewer])
                db.session.commit()

                records = [
                    FinancialRecord(amount=85000, type='income', category='Salary', date=date(2026, 3, 1), notes='March salary', created_by=1),
                    FinancialRecord(amount=45000, type='income', category='Freelance', date=date(2026, 3, 10), notes='', created_by=1),
                    FinancialRecord(amount=22000, type='expense', category='Rent', date=date(2026, 3, 5), notes='Office rent', created_by=1),
                    FinancialRecord(amount=8500, type='expense', category='Utilities', date=date(2026, 3, 12), notes='', created_by=1),
                    FinancialRecord(amount=12000, type='expense', category='Marketing', date=date(2026, 3, 15), notes='', created_by=1),
                    FinancialRecord(amount=35000, type='income', category='Investment', date=date(2026, 3, 20), notes='', created_by=1),
                ]
                db.session.add_all(records)
                db.session.commit()
                print("✅ MySQL Database seeded successfully!")
    except Exception as e:
        print(f"❌ Database Error: {str(e)}")
        print("→ Make sure MySQL server is running and password is correct.")

create_tables_and_seed()

if __name__ == '__main__':
    app.run(debug=True)