import json
import random
import string
import hashlib
from pathlib import Path
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import plotly.express as px
import plotly.graph_objects as go

import os
import sys


class Bank:
    # Dynamic database path for executable
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        database = os.path.join(os.path.dirname(sys.executable), 'data.json')
    else:
        # Running as script
        database = 'data.json'

    @staticmethod
    def _load_data():
        try:
            # Ensure the directory exists
            db_path = Bank.database
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)

            if os.path.exists(db_path):
                with open(db_path, 'r', encoding='utf-8') as fs:
                    content = fs.read().strip()
                    if not content:
                        return []
                    return json.loads(content)
            return []
        except Exception as err:
            # Create fresh data file if there's an error
            print(f"⚠️ Creating new database: {err}")
            return []

    # ... rest of your code remains same

    # ... rest of your Bank class remains the same

    @staticmethod
    def _hash_pin(pin):
        return hashlib.sha256(str(pin).encode()).hexdigest()

    @staticmethod
    def _load_data():
        try:
            if Path(Bank.database).exists():
                with open(Bank.database, 'r') as fs:
                    content = fs.read().strip()
                    if not content:
                        return []
                    return json.loads(content)
            return []
        except json.JSONDecodeError:
            st.warning("⚠️ Data file corrupted. Creating new database...")
            if Path(Bank.database).exists():
                Path(Bank.database).rename(f"{Bank.database}.backup")
            return []
        except Exception as err:
            st.error(f"Error loading data: {err}")
            return []

    @staticmethod
    def _save_data(data):
        try:
            with open(Bank.database, 'w') as fs:
                json.dump(data, fs, indent=2)
            return True
        except Exception as err:
            st.error(f"Error saving data: {err}")
            return False

    @staticmethod
    def _generate_account_number():
        alpha = random.choices(string.ascii_uppercase, k=4)
        num = random.choices(string.digits, k=6)
        return "".join(alpha + num)

    @staticmethod
    def _generate_card_number():
        return "".join([str(random.randint(0, 9)) for _ in range(16)])

    @staticmethod
    def _generate_cvv():
        return "".join([str(random.randint(0, 9)) for _ in range(3)])

    @staticmethod
    def _generate_otp():
        return "".join([str(random.randint(0, 9)) for _ in range(6)])

    @staticmethod
    def _generate_loan_id():
        return "LN" + "".join([str(random.randint(0, 9)) for _ in range(8)])

    @staticmethod
    def _find_user(account_no, pin):
        data = Bank._load_data()
        hashed_pin = Bank._hash_pin(pin)
        for user in data:
            if user['accountNo'] == account_no and user['pin'] == hashed_pin:
                return user, data
        return None, data

    @staticmethod
    def _find_user_by_account(account_no):
        data = Bank._load_data()
        for user in data:
            if user['accountNo'] == account_no:
                return user
        return None

    @staticmethod
    def create_account(name, age, email, mobile, address, pin):
        if age < 18:
            return False, "You must be 18 or older."
        if len(str(pin)) != 4 or not str(pin).isdigit():
            return False, "PIN must be 4 digits."
        if not name or not email or not mobile or not address:
            return False, "All fields required."
        if '@' not in email or '.' not in email:
            return False, "Invalid email."
        if len(str(mobile)) != 10 or not str(mobile).isdigit():
            return False, "Mobile must be 10 digits."

        data = Bank._load_data()
        card_number = Bank._generate_card_number()
        cvv = Bank._generate_cvv()
        expiry = (datetime.now() + timedelta(days=1825)).strftime("%m/%y")

        account_info = {
            "name": name,
            "age": age,
            "email": email,
            "mobile": mobile,
            "address": address,
            "pin": Bank._hash_pin(pin),
            "accountNo": Bank._generate_account_number(),
            "balance": 0,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "transactions": [],
            "virtual_card": {
                "card_number": card_number,
                "cvv": cvv,
                "expiry": expiry,
                "card_holder": name.upper()
            },
            "savings_goals": [],
            "beneficiaries": [],
            "loans": [],
            "bills": []
        }

        data.append(account_info)
        if Bank._save_data(data):
            return True, account_info['accountNo']
        return False, "Failed to create account."

    @staticmethod
    def deposit_money(account_no, pin, amount):
        user, data = Bank._find_user(account_no, pin)
        if not user:
            return False, "Invalid credentials."
        if amount <= 0:
            return False, "Amount must be > 0."
        if amount > 50000:
            return False, "Max ₹50,000 per deposit."

        user['balance'] += amount
        user['transactions'].append({
            "type": "deposit",
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "balance": user['balance'],
            "description": "Cash Deposit"
        })

        if Bank._save_data(data):
            return True, f"Deposited ₹{amount:,.0f}. Balance: ₹{user['balance']:,.0f}"
        return False, "Transaction failed."

    @staticmethod
    def withdraw_money(account_no, pin, amount):
        user, data = Bank._find_user(account_no, pin)
        if not user:
            return False, "Invalid credentials."
        if amount <= 0:
            return False, "Amount must be > 0."
        if user['balance'] < amount:
            return False, f"Insufficient balance. Available: ₹{user['balance']:,.0f}"

        user['balance'] -= amount
        user['transactions'].append({
            "type": "withdrawal",
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "balance": user['balance'],
            "description": "Cash Withdrawal"
        })

        if Bank._save_data(data):
            return True, f"Withdrew ₹{amount:,.0f}. Balance: ₹{user['balance']:,.0f}"
        return False, "Transaction failed."

    @staticmethod
    def transfer_money(from_account, pin, to_account, amount, description=""):
        sender, data = Bank._find_user(from_account, pin)
        if not sender:
            return False, "Invalid sender credentials."

        recipient = Bank._find_user_by_account(to_account)
        if not recipient:
            return False, "Recipient not found."
        if from_account == to_account:
            return False, "Cannot transfer to same account."
        if amount <= 0:
            return False, "Amount must be > 0."
        if sender['balance'] < amount:
            return False, f"Insufficient balance. Available: ₹{sender['balance']:,.0f}"
        if amount > 100000:
            return False, "Max ₹1,00,000 per transfer."

        sender['balance'] -= amount
        recipient['balance'] += amount
        transaction_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        transfer_desc = description if description else "Money Transfer"

        sender['transactions'].append({
            "type": "transfer_out",
            "amount": amount,
            "date": transaction_time,
            "balance": sender['balance'],
            "to_account": to_account,
            "recipient_name": recipient['name'],
            "description": transfer_desc
        })

        recipient['transactions'].append({
            "type": "transfer_in",
            "amount": amount,
            "date": transaction_time,
            "balance": recipient['balance'],
            "from_account": from_account,
            "sender_name": sender['name'],
            "description": transfer_desc
        })

        if Bank._save_data(data):
            return True, f"Transferred ₹{amount:,.0f} to {recipient['name']}. Balance: ₹{sender['balance']:,.0f}"
        return False, "Transfer failed."

    @staticmethod
    def add_beneficiary(account_no, pin, beneficiary_account, nickname):
        user, data = Bank._find_user(account_no, pin)
        if not user:
            return False, "Invalid credentials."

        if account_no == beneficiary_account:
            return False, "Cannot add yourself as beneficiary."

        beneficiary = Bank._find_user_by_account(beneficiary_account)
        if not beneficiary:
            return False, "Beneficiary account not found."

        if 'beneficiaries' not in user:
            user['beneficiaries'] = []

        for ben in user['beneficiaries']:
            if ben['account'] == beneficiary_account:
                return False, "Beneficiary already exists."

        user['beneficiaries'].append({
            "id": len(user['beneficiaries']) + 1,
            "account": beneficiary_account,
            "name": beneficiary['name'],
            "nickname": nickname,
            "added_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        if Bank._save_data(data):
            return True, f"Added {nickname} ({beneficiary['name']}) as beneficiary!"
        return False, "Failed to add beneficiary."

    @staticmethod
    def remove_beneficiary(account_no, pin, beneficiary_id):
        user, data = Bank._find_user(account_no, pin)
        if not user:
            return False, "Invalid credentials."

        beneficiaries = user.get('beneficiaries', [])
        user['beneficiaries'] = [b for b in beneficiaries if b['id'] != beneficiary_id]

        if Bank._save_data(data):
            return True, "Beneficiary removed!"
        return False, "Failed to remove beneficiary."

    @staticmethod
    def pay_bill(account_no, pin, bill_type, provider, bill_number, amount):
        user, data = Bank._find_user(account_no, pin)
        if not user:
            return False, "Invalid credentials."

        if amount <= 0:
            return False, "Amount must be > 0."

        if user['balance'] < amount:
            return False, f"Insufficient balance. Available: ₹{user['balance']:,.0f}"

        user['balance'] -= amount

        if 'bills' not in user:
            user['bills'] = []

        bill_record = {
            "id": len(user['bills']) + 1,
            "type": bill_type,
            "provider": provider,
            "bill_number": bill_number,
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Paid"
        }

        user['bills'].append(bill_record)

        user['transactions'].append({
            "type": "bill_payment",
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "balance": user['balance'],
            "description": f"{bill_type} - {provider}"
        })

        if Bank._save_data(data):
            return True, f"Bill paid successfully! ₹{amount:,.0f} | Balance: ₹{user['balance']:,.0f}"
        return False, "Bill payment failed."

    @staticmethod
    def calculate_emi(principal, rate, tenure_months):
        r = rate / (12 * 100)
        emi = principal * r * pow(1 + r, tenure_months) / (pow(1 + r, tenure_months) - 1)
        total_amount = emi * tenure_months
        total_interest = total_amount - principal
        return round(emi, 2), round(total_amount, 2), round(total_interest, 2)

    @staticmethod
    def apply_loan(account_no, pin, loan_type, amount, tenure_months, purpose):
        user, data = Bank._find_user(account_no, pin)
        if not user:
            return False, "Invalid credentials.", 0

        if amount < 10000:
            return False, "Minimum loan amount is ₹10,000.", 0

        if amount > 5000000:
            return False, "Maximum loan amount is ₹50,00,000.", 0

        rates = {
            "Personal Loan": 12.5,
            "Home Loan": 8.5,
            "Car Loan": 10.0,
            "Education Loan": 9.0
        }

        rate = rates.get(loan_type, 12.0)
        emi, total_amount, total_interest = Bank.calculate_emi(amount, rate, tenure_months)

        if 'loans' not in user:
            user['loans'] = []

        loan = {
            "loan_id": Bank._generate_loan_id(),
            "type": loan_type,
            "principal": amount,
            "interest_rate": rate,
            "tenure_months": tenure_months,
            "emi": emi,
            "total_amount": total_amount,
            "total_interest": total_interest,
            "outstanding": amount,
            "paid_emis": 0,
            "purpose": purpose,
            "applied_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Active",
            "next_emi_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        }

        user['loans'].append(loan)

        user['balance'] += amount
        user['transactions'].append({
            "type": "loan_credit",
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "balance": user['balance'],
            "description": f"Loan Disbursed - {loan_type}"
        })

        if Bank._save_data(data):
            return True, loan['loan_id'], emi
        return False, "Loan application failed.", 0

    @staticmethod
    def pay_emi(account_no, pin, loan_id):
        user, data = Bank._find_user(account_no, pin)
        if not user:
            return False, "Invalid credentials."

        loan = next((l for l in user.get('loans', []) if l['loan_id'] == loan_id), None)
        if not loan:
            return False, "Loan not found."

        if loan['status'] == 'Closed':
            return False, "Loan already closed."

        emi_amount = loan['emi']

        if user['balance'] < emi_amount:
            return False, f"Insufficient balance. EMI: ₹{emi_amount:,.2f}"

        user['balance'] -= emi_amount
        loan['paid_emis'] += 1

        principal_part = emi_amount - (loan['outstanding'] * loan['interest_rate'] / (12 * 100))
        loan['outstanding'] = max(0, loan['outstanding'] - principal_part)

        if loan['paid_emis'] >= loan['tenure_months'] or loan['outstanding'] <= 0:
            loan['status'] = 'Closed'
            loan['outstanding'] = 0
        else:
            next_date = datetime.strptime(loan['next_emi_date'], "%Y-%m-%d") + timedelta(days=30)
            loan['next_emi_date'] = next_date.strftime("%Y-%m-%d")

        user['transactions'].append({
            "type": "emi_payment",
            "amount": emi_amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "balance": user['balance'],
            "description": f"EMI Paid - {loan['type']}"
        })

        if Bank._save_data(data):
            status = "Loan Closed!" if loan['status'] == 'Closed' else f"EMI Paid! Remaining: {loan['tenure_months'] - loan['paid_emis']} EMIs"
            return True, status
        return False, "EMI payment failed."

    @staticmethod
    def close_loan(account_no, pin, loan_id):
        user, data = Bank._find_user(account_no, pin)
        if not user:
            return False, "Invalid credentials."

        loan = next((l for l in user.get('loans', []) if l['loan_id'] == loan_id), None)
        if not loan:
            return False, "Loan not found."

        if loan['status'] == 'Closed':
            return False, "Loan already closed."

        outstanding = loan['outstanding']

        if user['balance'] < outstanding:
            return False, f"Insufficient balance. Outstanding: ₹{outstanding:,.2f}"

        user['balance'] -= outstanding
        loan['status'] = 'Closed'
        loan['outstanding'] = 0

        user['transactions'].append({
            "type": "loan_closure",
            "amount": outstanding,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "balance": user['balance'],
            "description": f"Loan Closed - {loan['type']}"
        })

        if Bank._save_data(data):
            return True, f"Loan closed! Paid ₹{outstanding:,.2f}. Balance: ₹{user['balance']:,.0f}"
        return False, "Loan closure failed."

    @staticmethod
    def add_savings_goal(account_no, pin, goal_name, target_amount, deadline):
        user, data = Bank._find_user(account_no, pin)
        if not user:
            return False, "Invalid credentials."

        if 'savings_goals' not in user:
            user['savings_goals'] = []

        goal = {
            "id": len(user['savings_goals']) + 1,
            "name": goal_name,
            "target_amount": target_amount,
            "current_amount": 0,
            "deadline": deadline,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "active"
        }

        user['savings_goals'].append(goal)

        if Bank._save_data(data):
            return True, "Goal added successfully!"
        return False, "Failed to add goal."

    @staticmethod
    def contribute_to_goal(account_no, pin, goal_id, amount):
        user, data = Bank._find_user(account_no, pin)
        if not user:
            return False, "Invalid credentials."
        if user['balance'] < amount:
            return False, "Insufficient balance."

        goal = next((g for g in user.get('savings_goals', []) if g['id'] == goal_id), None)
        if not goal:
            return False, "Goal not found."
        if goal['status'] == 'completed':
            return False, "Goal already completed."

        user['balance'] -= amount
        goal['current_amount'] += amount

        if goal['current_amount'] >= goal['target_amount']:
            goal['status'] = 'completed'

        user['transactions'].append({
            "type": "savings_contribution",
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "balance": user['balance'],
            "description": f"Saved for: {goal['name']}"
        })

        if Bank._save_data(data):
            return True, f"Contributed ₹{amount:,.0f} to {goal['name']}!"
        return False, "Contribution failed."

    @staticmethod
    def get_details(account_no, pin):
        user, _ = Bank._find_user(account_no, pin)
        if not user:
            return None, "Invalid credentials."
        return user, "Success"

    @staticmethod
    def update_details(account_no, pin, name=None, email=None, mobile=None, address=None, new_pin=None):
        user, data = Bank._find_user(account_no, pin)
        if not user:
            return False, "Invalid credentials."

        if name:
            user['name'] = name
        if email:
            if '@' not in email or '.' not in email:
                return False, "Invalid email."
            user['email'] = email
        if mobile:
            if len(str(mobile)) != 10 or not str(mobile).isdigit():
                return False, "Mobile must be 10 digits."
            user['mobile'] = mobile
        if address:
            user['address'] = address
        if new_pin and len(str(new_pin)) == 4 and str(new_pin).isdigit():
            user['pin'] = Bank._hash_pin(new_pin)
        elif new_pin:
            return False, "PIN must be 4 digits."

        if Bank._save_data(data):
            return True, "Updated successfully."
        return False, "Update failed."

    @staticmethod
    def delete_account(account_no, pin):
        user, data = Bank._find_user(account_no, pin)
        if not user:
            return False, "Invalid credentials."
        data.remove(user)
        if Bank._save_data(data):
            return True, "Account deleted."
        return False, "Deletion failed."

    @staticmethod
    def filter_transactions(account_no, pin, start_date=None, end_date=None, txn_type=None, min_amount=None,
                            max_amount=None):
        user, _ = Bank._find_user(account_no, pin)
        if not user:
            return None, "Invalid credentials."

        transactions = user.get('transactions', [])
        filtered = []

        for txn in transactions:
            txn_date = datetime.strptime(txn['date'], "%Y-%m-%d %H:%M:%S")
            if start_date and txn_date < start_date:
                continue
            if end_date and txn_date > end_date:
                continue
            if txn_type and txn_type != "all" and txn['type'] != txn_type:
                continue
            if min_amount and txn['amount'] < min_amount:
                continue
            if max_amount and txn['amount'] > max_amount:
                continue
            filtered.append(txn)

        return filtered, "Success"

    @staticmethod
    def generate_statement_pdf(user, transactions, start_date=None, end_date=None):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24,
                                     textColor=colors.HexColor('#667eea'), spaceAfter=30,
                                     alignment=TA_CENTER, fontName='Helvetica-Bold')

        elements.append(Paragraph("BANK STATEMENT", title_style))
        elements.append(Spacer(1, 0.3 * inch))

        account_info = [
            ['Account Holder:', user['name']],
            ['Account Number:', user['accountNo']],
            ['Email:', user['email']],
            ['Mobile:', user.get('mobile', 'N/A')],
            ['Address:', user.get('address', 'N/A')],
            ['Balance:', f"Rs.{user['balance']:,.2f}"],
            ['Date:', datetime.now().strftime("%Y-%m-%d")],
        ]

        info_table = Table(account_info, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        elements.append(info_table)
        elements.append(Spacer(1, 0.5 * inch))

        if transactions:
            txn_data = [['Date', 'Type', 'Amount', 'Balance']]
            for txn in reversed(transactions):
                txn_type = txn['type'].replace('_', ' ').title()
                amount_str = f"Rs.{txn['amount']:,.2f}"
                if txn['type'] in ['withdrawal', 'transfer_out', 'savings_contribution', 'bill_payment', 'emi_payment',
                                   'loan_closure']:
                    amount_str = f"-{amount_str}"
                else:
                    amount_str = f"+{amount_str}"
                txn_data.append([txn['date'], txn_type, amount_str, f"Rs.{txn['balance']:,.2f}"])

            txn_table = Table(txn_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
            txn_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            elements.append(txn_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer


def load_css(dark_mode=False):
    if dark_mode:
        st.markdown("""<style>
            .main { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }
            .custom-card { background: #0f3460; color: white; border-radius: 15px; padding: 25px; margin: 10px 0; }
            h1, h2, h3 { color: #e94560 !important; }
            </style>""", unsafe_allow_html=True)
    else:
        st.markdown("""<style>
            .main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .custom-card { background: white; border-radius: 15px; padding: 25px; margin: 10px 0; }
            .stButton>button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                               color: white; border-radius: 10px; padding: 10px 30px; }
            [data-testid="stSidebar"] { background: linear-gradient(180deg, #667eea 0%, #764ba2 100%); }
            [data-testid="stSidebar"] * { color: white !important; }
            </style>""", unsafe_allow_html=True)


def create_transaction_chart(transactions):
    if not transactions:
        return None
    df_data = [{'Date': datetime.strptime(txn['date'], "%Y-%m-%d %H:%M:%S"),
                'Balance': txn['balance']} for txn in transactions]
    df = pd.DataFrame(df_data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Balance'], mode='lines+markers',
                             name='Balance', line=dict(color='#667eea', width=3)))
    fig.update_layout(title='Balance Trend', xaxis_title='Date', yaxis_title='Balance (Rs.)', height=400)
    return fig


def create_transaction_pie_chart(transactions):
    if not transactions:
        return None
    type_counts = {}
    for txn in transactions:
        t = txn['type'].replace('_', ' ').title()
        type_counts[t] = type_counts.get(t, 0) + 1
    fig = px.pie(values=list(type_counts.values()), names=list(type_counts.keys()), title='Transaction Distribution')
    fig.update_layout(height=400)
    return fig


def main():
    st.set_page_config(page_title="Bank Management", page_icon="🏦", layout="wide")

    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'otp_code' not in st.session_state:
        st.session_state.otp_code = None
    if 'otp_email' not in st.session_state:
        st.session_state.otp_email = None
    if 'otp_time' not in st.session_state:
        st.session_state.otp_time = None

    load_css(st.session_state.dark_mode)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        if st.button("🌙" if not st.session_state.dark_mode else "☀️"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 15px; margin-bottom: 30px;'>
            <h1 style='color: white; text-align: center; margin: 0;'>
                🏦 Ultimate Bank Management System
            </h1>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### 📋 Menu")
        menu = st.selectbox("Select Operation", [
            "🏠 Home", "➕ Create", "💰 Deposit", "💸 Withdraw",
            "🔄 Transfer", "👥 Beneficiaries", "💡 Bill Payment",
            "💳 Loans", "📊 Details", "📈 Analytics",
            "🔍 Search", "💳 Card", "🎯 Goals", "✏️ Update", "🗑️ Delete"
        ])

    menu_clean = menu.split(" ", 1)[1]

    if "Home" in menu_clean:
        data = Bank._load_data()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='custom-card'><h3>👥 Accounts</h3><h1>{len(data)}</h1></div>",
                        unsafe_allow_html=True)
        with col2:
            st.markdown(
                f"<div class='custom-card'><h3>💵 Total Balance</h3><h1>₹{sum(u['balance'] for u in data):,.0f}</h1></div>",
                unsafe_allow_html=True)
        with col3:
            st.markdown(
                f"<div class='custom-card'><h3>📈 Transactions</h3><h1>{sum(len(u.get('transactions', [])) for u in data)}</h1></div>",
                unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            total_loans = sum(len(u.get('loans', [])) for u in data)
            st.markdown(f"<div class='custom-card'><h3>💳 Active Loans</h3><h1>{total_loans}</h1></div>",
                        unsafe_allow_html=True)
        with col2:
            total_beneficiaries = sum(len(u.get('beneficiaries', [])) for u in data)
            st.markdown(f"<div class='custom-card'><h3>👥 Beneficiaries</h3><h1>{total_beneficiaries}</h1></div>",
                        unsafe_allow_html=True)
        with col3:
            total_goals = sum(len(u.get('savings_goals', [])) for u in data)
            st.markdown(f"<div class='custom-card'><h3>🎯 Savings Goals</h3><h1>{total_goals}</h1></div>",
                        unsafe_allow_html=True)

    elif "Create" in menu_clean:
        st.markdown("### ➕ Create Account")

        if st.session_state.otp_code is None:
            st.info("📝 Step 1: Fill your details")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("👤 Name")
                email = st.text_input("📧 Email")
                mobile = st.text_input("📱 Mobile", max_chars=10)
            with col2:
                age = st.number_input("🎂 Age", min_value=18, value=18)
                pin = st.text_input("🔒 PIN", type="password", max_chars=4)
                address = st.text_area("🏠 Address")

            if st.button("📧 Send OTP", use_container_width=True):
                if not name or not email or not mobile or not address or not pin:
                    st.error("❌ Please fill all fields!")
                elif '@' not in email or '.' not in email:
                    st.error("❌ Invalid email!")
                elif len(str(mobile)) != 10:
                    st.error("❌ Mobile must be 10 digits!")
                elif len(str(pin)) != 4:
                    st.error("❌ PIN must be 4 digits!")
                else:
                    otp = Bank._generate_otp()
                    st.session_state.otp_code = otp
                    st.session_state.otp_email = email
                    st.session_state.otp_time = datetime.now()
                    st.session_state.temp_data = {'name': name, 'age': age, 'email': email,
                                                  'mobile': mobile, 'address': address, 'pin': pin}
                    st.rerun()
        else:
            st.info("📝 Step 2: Verify OTP")
            st.success(f"📧 OTP sent to: {st.session_state.otp_email}")

            st.markdown(f"""
                <div style='background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%); 
                            padding: 30px;
                            border-radius: 15px;
                            text-align: center;
                            margin: 20px 0;
                            box-shadow: 0 10px 30px rgba(0,0,0,0.3);'>
                    <h2 style='color: white; margin: 0;'>🔐 Your OTP Code</h2>
                    <h1 style='color: white; font-size: 48px; letter-spacing: 10px; margin: 20px 0;'>
                        {st.session_state.otp_code}
                    </h1>
                    <p style='color: white; margin: 0;'>⏰ Valid for 5 minutes | Copy this code</p>
                </div>
            """, unsafe_allow_html=True)

            time_left = 300 - (datetime.now() - st.session_state.otp_time).seconds

            if time_left > 0:
                st.warning(f"⏰ Time remaining: {time_left // 60} minutes {time_left % 60} seconds")

                otp_input = st.text_input("🔐 Enter the 6-digit OTP shown above", max_chars=6, key="otp_verify")

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✅ Verify & Create", use_container_width=True):
                        if otp_input == st.session_state.otp_code:
                            d = st.session_state.temp_data
                            success, msg = Bank.create_account(d['name'], d['age'], d['email'],
                                                               d['mobile'], d['address'], d['pin'])
                            if success:
                                st.balloons()
                                st.success(f"🎉 Account Created!")
                                st.markdown(f"""
                                    <div style='background: #d4edda; padding: 20px; border-radius: 10px; 
                                                border-left: 5px solid #28a745; margin: 20px 0;'>
                                        <h3 style='color: #155724; margin: 0;'>Your Account Number</h3>
                                        <h1 style='color: #155724; font-size: 36px; letter-spacing: 3px; margin: 10px 0;'>
                                            {msg}
                                        </h1>
                                        <p style='color: #155724; margin: 0;'>⚠️ Please save this!</p>
                                    </div>
                                """, unsafe_allow_html=True)
                                st.session_state.otp_code = None
                                st.session_state.temp_data = None
                            else:
                                st.error(f"❌ {msg}")
                        else:
                            st.error("❌ Invalid OTP!")
                with col2:
                    if st.button("🔄 Resend OTP", use_container_width=True):
                        otp = Bank._generate_otp()
                        st.session_state.otp_code = otp
                        st.session_state.otp_time = datetime.now()
                        st.success(f"✅ New OTP sent!")
                        st.rerun()
                with col3:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.otp_code = None
                        st.session_state.otp_email = None
                        st.session_state.otp_time = None
                        st.session_state.temp_data = None
                        st.rerun()
            else:
                st.error("⏰ OTP Expired!")
                if st.button("🔄 Start Over", use_container_width=True):
                    st.session_state.otp_code = None
                    st.session_state.otp_email = None
                    st.session_state.otp_time = None
                    st.session_state.temp_data = None
                    st.rerun()

    elif "Deposit" in menu_clean:
        st.markdown("### 💰 Deposit Money")
        with st.form("deposit"):
            account_no = st.text_input("🏦 Account Number")
            pin = st.text_input("🔒 PIN", type="password", max_chars=4)
            amount = st.number_input("💵 Amount", min_value=1, value=1000)
            if st.form_submit_button("💰 Deposit"):
                success, msg = Bank.deposit_money(account_no, pin, amount)
                if success:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)

    elif "Withdraw" in menu_clean:
        st.markdown("### 💸 Withdraw Money")
        with st.form("withdraw"):
            account_no = st.text_input("🏦 Account Number")
            pin = st.text_input("🔒 PIN", type="password", max_chars=4)
            amount = st.number_input("💵 Amount", min_value=1, value=500)
            if st.form_submit_button("💸 Withdraw"):
                success, msg = Bank.withdraw_money(account_no, pin, amount)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

    elif "Transfer" in menu_clean:
        st.markdown("### 🔄 Transfer Money")
        with st.form("transfer"):
            col1, col2 = st.columns(2)
            with col1:
                from_acc = st.text_input("From Account")
                pin = st.text_input("PIN", type="password", max_chars=4)
            with col2:
                to_acc = st.text_input("To Account")
                amount = st.number_input("Amount", min_value=1, value=1000)
            desc = st.text_input("Description (Optional)")
            if st.form_submit_button("🔄 Transfer"):
                success, msg = Bank.transfer_money(from_acc, pin, to_acc, amount, desc)
                if success:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)

    elif "Beneficiaries" in menu_clean:
        st.markdown("### 👥 Manage Beneficiaries")
        tab1, tab2 = st.tabs(["View Beneficiaries", "Add New"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                account_no = st.text_input("Account Number", key="view_ben_acc")
            with col2:
                pin = st.text_input("PIN", type="password", max_chars=4, key="view_ben_pin")

            if st.button("View Beneficiaries", key="view_ben_btn"):
                user, msg = Bank.get_details(account_no, pin)
                if user:
                    beneficiaries = user.get('beneficiaries', [])
                    if beneficiaries:
                        st.success(f"📋 You have {len(beneficiaries)} beneficiaries")
                        for ben in beneficiaries:
                            with st.container():
                                st.markdown(f"### 💼 {ben['nickname']} - {ben['name']}")
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.info(f"**Account:** {ben['account']}")
                                with col2:
                                    st.info(f"**Added:** {ben['added_on'][:10]}")
                                with col3:
                                    if st.button(f"🗑️ Remove", key=f"rem_{ben['id']}"):
                                        success, m = Bank.remove_beneficiary(account_no, pin, ben['id'])
                                        if success:
                                            st.success(m)
                                            st.rerun()
                                        else:
                                            st.error(m)

                                st.markdown("**Quick Transfer**")
                                col1, col2 = st.columns(2)
                                with col1:
                                    transfer_amt = st.number_input("Amount", min_value=1, value=1000,
                                                                   key=f"amt_{ben['id']}")
                                with col2:
                                    transfer_desc = st.text_input("Description", placeholder="Optional",
                                                                  key=f"desc_{ben['id']}")
                                if st.button(f"💸 Transfer ₹{transfer_amt:,.0f}", key=f"trans_{ben['id']}"):
                                    success, m = Bank.transfer_money(account_no, pin, ben['account'],
                                                                     transfer_amt, transfer_desc)
                                    if success:
                                        st.success(m)
                                        st.balloons()
                                    else:
                                        st.error(m)
                                st.markdown("---")
                    else:
                        st.info("🔭 No beneficiaries yet")
                else:
                    st.error(msg)

        with tab2:
            with st.form("add_beneficiary"):
                col1, col2 = st.columns(2)
                with col1:
                    account_no = st.text_input("Your Account", key="add_acc")
                    beneficiary_acc = st.text_input("Beneficiary Account")
                with col2:
                    pin = st.text_input("PIN", type="password", max_chars=4, key="add_pin")
                    nickname = st.text_input("Nickname", placeholder="e.g., Mom, Dad")

                if st.form_submit_button("➕ Add Beneficiary"):
                    if not nickname:
                        st.error("❌ Please provide a nickname")
                    else:
                        success, msg = Bank.add_beneficiary(account_no, pin, beneficiary_acc, nickname)
                        if success:
                            st.success(msg)
                            st.balloons()
                        else:
                            st.error(msg)

    elif "Bill Payment" in menu_clean:
        st.markdown("### 💡 Pay Bills")

        with st.form("bill_payment"):
            col1, col2 = st.columns(2)
            with col1:
                account_no = st.text_input("Account Number")
                pin = st.text_input("PIN", type="password", max_chars=4)
            with col2:
                bill_type = st.selectbox("Bill Type", [
                    "Electricity", "Water", "Gas", "Mobile Recharge",
                    "DTH", "Broadband", "Credit Card"
                ])
                amount = st.number_input("Amount", min_value=1, value=500)

            provider = st.text_input("Provider Name", placeholder="e.g., Airtel, UPPCL")
            bill_number = st.text_input("Bill/Mobile Number")

            if st.form_submit_button("💳 Pay Bill"):
                if not provider or not bill_number:
                    st.error("❌ Please fill all details")
                else:
                    success, msg = Bank.pay_bill(account_no, pin, bill_type, provider,
                                                 bill_number, amount)
                    if success:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)

        st.markdown("---")
        st.markdown("### 📜 Recent Bills")

        col1, col2 = st.columns(2)
        with col1:
            account_no_view = st.text_input("Account", key="bill_view_acc")
        with col2:
            pin_view = st.text_input("PIN", type="password", max_chars=4, key="bill_view_pin")

        if st.button("View History", key="view_bills_btn"):
            user, msg = Bank.get_details(account_no_view, pin_view)
            if user:
                bills = user.get('bills', [])
                if bills:
                    bills_data = [{
                        "Date": b['date'][:10],
                        "Type": b['type'],
                        "Provider": b['provider'],
                        "Amount": f"₹{b['amount']:,.0f}",
                        "Status": b['status']
                    } for b in reversed(bills[-10:])]
                    st.dataframe(pd.DataFrame(bills_data), use_container_width=True, hide_index=True)
                else:
                    st.info("🔭 No bills yet")
            else:
                st.error(msg)

    elif "Loans" in menu_clean:
        st.markdown("### 💳 Loan Management")
        tab1, tab2, tab3, tab4 = st.tabs(["Apply Loan", "My Loans", "Pay Loan/EMI", "EMI Calculator"])

        with tab1:
            st.markdown("#### 📝 Apply for Loan")
            with st.form("apply_loan"):
                col1, col2 = st.columns(2)
                with col1:
                    account_no = st.text_input("Account Number")
                    pin = st.text_input("PIN", type="password", max_chars=4)
                    loan_type = st.selectbox("Loan Type", [
                        "Personal Loan", "Home Loan", "Car Loan", "Education Loan"
                    ])
                with col2:
                    amount = st.number_input("Amount", min_value=10000, max_value=5000000,
                                             value=100000, step=10000)
                    tenure = st.number_input("Tenure (Months)", min_value=6, max_value=360, value=12)
                    purpose = st.text_input("Purpose", placeholder="e.g., Car purchase")

                rates = {"Personal Loan": 12.5, "Home Loan": 8.5, "Car Loan": 10.0, "Education Loan": 9.0}
                st.info(f"📊 Rate: {rates[loan_type]}% p.a.")

                if st.form_submit_button("🎯 Apply"):
                    if not purpose:
                        st.error("❌ Please specify purpose")
                    else:
                        success, loan_id, emi = Bank.apply_loan(account_no, pin, loan_type,
                                                                amount, tenure, purpose)
                        if success:
                            st.success("🎉 Loan Approved!")
                            st.balloons()
                            st.markdown(f"""
                                <div style='background: #d4edda; padding: 20px; border-radius: 10px; 
                                            border-left: 5px solid #28a745; margin: 20px 0;'>
                                    <h3 style='color: #155724;'>Loan Details</h3>
                                    <p style='color: #155724;'><b>ID:</b> {loan_id}</p>
                                    <p style='color: #155724;'><b>Amount:</b> ₹{amount:,.0f}</p>
                                    <p style='color: #155724;'><b>EMI:</b> ₹{emi:,.2f}</p>
                                    <p style='color: #155724;'><b>Tenure:</b> {tenure} months</p>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(loan_id)

        with tab2:
            st.markdown("#### 📊 Your Loans")
            col1, col2 = st.columns(2)
            with col1:
                account_no = st.text_input("Account", key="loan_acc")
            with col2:
                pin = st.text_input("PIN", type="password", max_chars=4, key="loan_pin")

            if st.button("View Loans", key="view_loans_btn"):
                user, msg = Bank.get_details(account_no, pin)
                if user:
                    loans = user.get('loans', [])
                    if loans:
                        active_loans = [l for l in loans if l['status'] != 'Closed']
                        closed_loans = [l for l in loans if l['status'] == 'Closed']

                        st.success(f"📊 Total: {len(loans)} | Active: {len(active_loans)} | Closed: {len(closed_loans)}")

                        if active_loans:
                            st.markdown("### ⏳ Active Loans")
                            for loan in active_loans:
                                st.markdown(f"### 🏦 {loan['type']} - {loan['loan_id']}")

                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("💵 Principal", f"₹{loan['principal']:,.0f}")
                                    st.metric("📊 Rate", f"{loan['interest_rate']}%")
                                with col2:
                                    st.metric("💳 EMI", f"₹{loan['emi']:,.2f}")
                                    st.metric("💰 Interest", f"₹{loan['total_interest']:,.0f}")
                                with col3:
                                    st.metric("✅ Paid", f"{loan['paid_emis']}/{loan['tenure_months']}")
                                    st.metric("⚠️ Outstanding", f"₹{loan['outstanding']:,.0f}")

                                progress = (loan['paid_emis'] / loan['tenure_months']) * 100
                                st.progress(min(progress / 100, 1.0))
                                st.info(f"📅 Next EMI: {loan['next_emi_date']}")

                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.info(f"💵 Balance: ₹{user['balance']:,.0f}")
                                with col2:
                                    if user['balance'] >= loan['emi']:
                                        if st.button(f"💰 Pay EMI", key=f"emi_{loan['loan_id']}", type="primary"):
                                            success, m = Bank.pay_emi(account_no, pin, loan['loan_id'])
                                            if success:
                                                st.success(m)
                                                st.balloons()
                                                st.rerun()
                                            else:
                                                st.error(m)
                                    else:
                                        st.error(f"❌ Low Balance")
                                with col3:
                                    if user['balance'] >= loan['outstanding']:
                                        if st.button(f"🔒 Close Loan", key=f"close_{loan['loan_id']}"):
                                            success, m = Bank.close_loan(account_no, pin, loan['loan_id'])
                                            if success:
                                                st.success(m)
                                                st.balloons()
                                                st.rerun()
                                            else:
                                                st.error(m)
                                    else:
                                        st.error(f"❌ Insufficient")
                                st.markdown("---")

                        if closed_loans:
                            st.markdown("### ✅ Closed Loans")
                            for loan in closed_loans:
                                with st.expander(f"✅ {loan['type']} - {loan['loan_id']}"):
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Principal", f"₹{loan['principal']:,.0f}")
                                    with col2:
                                        st.metric("Interest Paid", f"₹{loan['total_interest']:,.0f}")
                                    with col3:
                                        st.metric("Status", "CLOSED ✅")
                    else:
                        st.info("🔭 No loans yet")
                else:
                    st.error(msg)

        with tab3:
            st.markdown("#### 💰 Pay Loan / EMI")
            st.info("💡 Pay monthly EMI or close entire loan at once")

            col1, col2 = st.columns(2)
            with col1:
                account_no_pay = st.text_input("Account Number", key="pay_loan_acc")
            with col2:
                pin_pay = st.text_input("PIN", type="password", max_chars=4, key="pay_loan_pin")

            if st.button("🔍 Show My Active Loans", key="show_loans_payment"):
                user, msg = Bank.get_details(account_no_pay, pin_pay)
                if user:
                    active_loans = [l for l in user.get('loans', []) if l['status'] != 'Closed']

                    if active_loans:
                        st.success(f"✅ You have {len(active_loans)} active loan(s)")

                        for idx, loan in enumerate(active_loans):
                            with st.expander(f"🏦 {loan['type']} - {loan['loan_id']}", expanded=True):
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("💵 Loan Amount", f"₹{loan['principal']:,.0f}")
                                with col2:
                                    st.metric("📊 Rate", f"{loan['interest_rate']}%")
                                with col3:
                                    st.metric("💳 EMI", f"₹{loan['emi']:,.2f}")
                                with col4:
                                    st.metric("⏳ Remaining", f"{loan['tenure_months'] - loan['paid_emis']} EMIs")

                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("✅ Paid", f"{loan['paid_emis']}/{loan['tenure_months']}")
                                with col2:
                                    st.metric("💰 Outstanding", f"₹{loan['outstanding']:,.0f}")

                                progress = (loan['paid_emis'] / loan['tenure_months']) * 100
                                st.progress(min(progress / 100, 1.0))
                                st.info(f"📅 Next EMI Due: {loan['next_emi_date']}")

                                st.markdown("---")
                                st.markdown("### 💳 Payment Options")

                                payment_type = st.radio(
                                    "Select Payment Type:",
                                    ["💰 Pay Single EMI", "🔒 Close Full Loan"],
                                    key=f"payment_type_{idx}",
                                    horizontal=True
                                )

                                if payment_type == "💰 Pay Single EMI":
                                    st.warning(f"⚠️ EMI Amount: ₹{loan['emi']:,.2f} will be deducted")
                                    st.info(f"💵 Your Balance: ₹{user['balance']:,.0f}")

                                    if user['balance'] < loan['emi']:
                                        st.error(f"❌ Insufficient balance! Need ₹{loan['emi']:,.2f}")
                                    else:
                                        if st.button(f"✅ Confirm - Pay EMI ₹{loan['emi']:,.2f}",
                                                     key=f"pay_emi_{idx}", type="primary"):
                                            success, msg_result = Bank.pay_emi(account_no_pay, pin_pay, loan['loan_id'])
                                            if success:
                                                st.success(f"🎉 {msg_result}")
                                                st.balloons()
                                                st.rerun()
                                            else:
                                                st.error(f"❌ {msg_result}")

                                else:
                                    st.warning(f"⚠️ Outstanding: ₹{loan['outstanding']:,.2f} will be deducted")
                                    st.info(f"💵 Your Balance: ₹{user['balance']:,.0f}")

                                    if user['balance'] < loan['outstanding']:
                                        st.error(f"❌ Insufficient balance! Need ₹{loan['outstanding']:,.2f}")
                                    else:
                                        confirm_close = st.checkbox(
                                            f"I confirm closing loan by paying ₹{loan['outstanding']:,.2f}",
                                            key=f"confirm_close_{idx}"
                                        )
                                        if confirm_close:
                                            if st.button(f"🔒 Close Loan Now",
                                                         key=f"close_loan_{idx}", type="primary"):
                                                success, msg_result = Bank.close_loan(account_no_pay, pin_pay,
                                                                                      loan['loan_id'])
                                                if success:
                                                    st.success(f"🎉 {msg_result}")
                                                    st.balloons()
                                                    st.rerun()
                                                else:
                                                    st.error(f"❌ {msg_result}")

                                st.markdown("---")
                    else:
                        st.info("✅ No active loans! You're debt-free! 🎉")
                else:
                    st.error(f"❌ {msg}")

            st.markdown("---")
            st.markdown("### ⚡ Quick EMI Payment")
            st.info("💡 Know your Loan ID? Pay directly!")

            with st.form("quick_emi_payment"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    quick_account = st.text_input("Account", key="quick_acc")
                with col2:
                    quick_pin = st.text_input("PIN", type="password", max_chars=4, key="quick_pin")
                with col3:
                    quick_loan_id = st.text_input("Loan ID", placeholder="LN12345678")

                if st.form_submit_button("💳 Pay EMI Now", use_container_width=True):
                    if not quick_loan_id:
                        st.error("❌ Please enter Loan ID")
                    else:
                        success, msg = Bank.pay_emi(quick_account, quick_pin, quick_loan_id)
                        if success:
                            st.success(f"🎉 {msg}")
                            st.balloons()
                        else:
                            st.error(f"❌ {msg}")

        with tab4:
            st.markdown("#### 🧮 EMI Calculator")
            st.info("💡 Calculate EMI before applying!")

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("##### 📊 Loan Details")

                calc_loan_type = st.selectbox("Loan Type", [
                    "Personal Loan (12.5%)",
                    "Home Loan (8.5%)",
                    "Car Loan (10.0%)",
                    "Education Loan (9.0%)",
                    "Custom Rate"
                ])

                col1a, col1b = st.columns(2)
                with col1a:
                    calc_amount = st.number_input("Amount (₹)",
                                                  min_value=10000,
                                                  max_value=10000000,
                                                  value=500000,
                                                  step=10000)
                with col1b:
                    calc_tenure = st.number_input("Tenure (Months)",
                                                  min_value=6,
                                                  max_value=360,
                                                  value=60)

                if "Personal" in calc_loan_type:
                    calc_rate = 12.5
                elif "Home" in calc_loan_type:
                    calc_rate = 8.5
                elif "Car" in calc_loan_type:
                    calc_rate = 10.0
                elif "Education" in calc_loan_type:
                    calc_rate = 9.0
                else:
                    calc_rate = st.number_input("Rate (%)", min_value=1.0, max_value=30.0, value=10.0, step=0.1)

                if "Custom" not in calc_loan_type:
                    st.info(f"📊 Interest Rate: **{calc_rate}%** p.a.")

            with col2:
                st.markdown("##### ⚡ Presets")
                if st.button("🏠 Home", use_container_width=True):
                    st.session_state.preset = "home"
                if st.button("🚗 Car", use_container_width=True):
                    st.session_state.preset = "car"
                if st.button("💼 Personal", use_container_width=True):
                    st.session_state.preset = "personal"

            st.markdown("---")

            if st.button("🧮 Calculate EMI", use_container_width=True, type="primary"):
                emi, total, interest = Bank.calculate_emi(calc_amount, calc_rate, calc_tenure)

                st.markdown("### 💰 Results")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📅 Monthly EMI", f"₹{emi:,.2f}")
                with col2:
                    st.metric("💵 Total Payment", f"₹{total:,.2f}",
                              delta=f"+₹{total - calc_amount:,.2f}")
                with col3:
                    st.metric("📊 Total Interest", f"₹{interest:,.2f}")

                st.markdown("---")
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.markdown("##### 📋 Summary")
                    summary = {
                        "Parameter": ["Principal", "Rate", "Tenure", "EMI", "Interest", "Total"],
                        "Value": [f"₹{calc_amount:,.0f}", f"{calc_rate}% p.a.",
                                  f"{calc_tenure} months", f"₹{emi:,.2f}",
                                  f"₹{interest:,.2f}", f"₹{total:,.2f}"]
                    }
                    st.dataframe(pd.DataFrame(summary), hide_index=True, use_container_width=True)

                    st.info(f"💡 Recommended Income: ₹{emi * 3:,.0f}+")

                with col2:
                    st.markdown("##### 📊 Breakdown")
                    fig = px.pie(
                        values=[calc_amount, interest],
                        names=['Principal', 'Interest'],
                        color_discrete_sequence=['#667eea', '#f5365c'],
                        hole=0.4
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)

    elif "Details" in menu_clean:
        st.markdown("### 📊 Account Details")
        col1, col2 = st.columns(2)
        with col1:
            account_no = st.text_input("Account")
        with col2:
            pin = st.text_input("PIN", type="password", max_chars=4)

        if st.button("View Details"):
            user, msg = Bank.get_details(account_no, pin)
            if user:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Name", user['name'])
                with col2:
                    st.metric("Balance", f"₹{user['balance']:,.0f}")
                with col3:
                    st.metric("Account", user['accountNo'])

                st.info(f"📧 {user['email']} | 📱 {user.get('mobile', 'N/A')}")

                if user.get('transactions'):
                    txn_data = [{"Type": t['type'], "Amount": f"₹{t['amount']:,.0f}",
                                 "Date": t['date']} for t in reversed(user['transactions'][-10:])]
                    st.dataframe(pd.DataFrame(txn_data), use_container_width=True, hide_index=True)
            else:
                st.error(msg)

    elif "Analytics" in menu_clean:
        st.markdown("### 📈 Analytics")
        col1, col2 = st.columns(2)
        with col1:
            account_no = st.text_input("Account")
        with col2:
            pin = st.text_input("PIN", type="password", max_chars=4)

        if st.button("View Analytics"):
            user, msg = Bank.get_details(account_no, pin)
            if user and user.get('transactions'):
                txns = user['transactions']
                col1, col2 = st.columns(2)
                with col1:
                    fig = create_transaction_chart(txns)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                with col2:
                    fig = create_transaction_pie_chart(txns)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(msg if not user else "No transactions")

    elif "Search" in menu_clean:
        st.markdown("### 🔍 Search Transactions")
        with st.form("search"):
            col1, col2 = st.columns(2)
            with col1:
                account_no = st.text_input("Account")
                start = st.date_input("From", value=None)
            with col2:
                pin = st.text_input("PIN", type="password", max_chars=4)
                end = st.date_input("To", value=None)
            submitted = st.form_submit_button("Search")

        if submitted:
            start_dt = datetime.combine(start, datetime.min.time()) if start else None
            end_dt = datetime.combine(end, datetime.max.time()) if end else None
            filtered, msg = Bank.filter_transactions(account_no, pin, start_dt, end_dt)
            if filtered:
                st.success(f"Found {len(filtered)} transactions")
                txn_data = [{"Type": t['type'], "Amount": f"₹{t['amount']:,.0f}",
                             "Date": t['date']} for t in reversed(filtered)]
                st.dataframe(pd.DataFrame(txn_data), use_container_width=True, hide_index=True)
            else:
                st.warning("No transactions")

    elif "Card" in menu_clean:
        st.markdown("### 💳 Virtual Card")
        col1, col2 = st.columns(2)
        with col1:
            account_no = st.text_input("Account")
        with col2:
            pin = st.text_input("PIN", type="password", max_chars=4)

        if st.button("View Card"):
            user, msg = Bank.get_details(account_no, pin)
            if user:
                card = user.get('virtual_card', {})
                if card:
                    st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    border-radius: 20px; padding: 30px; color: white;
                                    box-shadow: 0 10px 30px rgba(0,0,0,0.3); max-width: 500px; margin: 20px auto;'>
                            <div style='font-size: 24px; margin-bottom: 30px;'>💳 BANK CARD</div>
                            <div style='font-size: 20px; letter-spacing: 3px; margin-bottom: 20px;'>
                                {card['card_number'][:4]} {card['card_number'][4:8]} {card['card_number'][8:12]} {card['card_number'][12:]}
                            </div>
                            <div style='display: flex; justify-content: space-between; margin-top: 30px;'>
                                <div>
                                    <div style='font-size: 12px; opacity: 0.8;'>HOLDER</div>
                                    <div style='font-size: 16px; font-weight: bold;'>{card['card_holder']}</div>
                                </div>
                                <div>
                                    <div style='font-size: 12px; opacity: 0.8;'>EXPIRES</div>
                                    <div style='font-size: 16px; font-weight: bold;'>{card['expiry']}</div>
                                </div>
                                <div>
                                    <div style='font-size: 12px; opacity: 0.8;'>CVV</div>
                                    <div style='font-size: 16px; font-weight: bold;'>{card['cvv']}</div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.error(msg)

    elif "Goals" in menu_clean:
        st.markdown("### 🎯 Savings Goals")
        tab1, tab2 = st.tabs(["View Goals", "Add Goal"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                account_no = st.text_input("Account", key="goal_acc")
            with col2:
                pin = st.text_input("PIN", type="password", max_chars=4, key="goal_pin")

            if st.button("View Goals"):
                user, msg = Bank.get_details(account_no, pin)
                if user:
                    goals = user.get('savings_goals', [])
                    if goals:
                        for goal in goals:
                            progress = (goal['current_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
                            status = "✅" if goal['status'] == 'completed' else "⏳"

                            st.markdown(f"### {status} {goal['name']}")

                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Target", f"₹{goal['target_amount']:,.0f}")
                            with col2:
                                st.metric("Saved", f"₹{goal['current_amount']:,.0f}")
                            with col3:
                                st.metric("Remaining", f"₹{goal['target_amount'] - goal['current_amount']:,.0f}")

                            st.progress(min(progress / 100, 1.0))

                            if goal['status'] != 'completed':
                                amt = st.number_input(f"Amount", min_value=1, value=100, key=f"c_{goal['id']}")
                                if st.button(f"Add ₹{amt:,.0f}", key=f"b_{goal['id']}"):
                                    success, m = Bank.contribute_to_goal(account_no, pin, goal['id'], amt)
                                    if success:
                                        st.success(m)
                                        st.rerun()
                            st.markdown("---")
                    else:
                        st.info("No goals yet")
                else:
                    st.error(msg)

        with tab2:
            with st.form("add_goal"):
                col1, col2 = st.columns(2)
                with col1:
                    account_no = st.text_input("Account")
                with col2:
                    pin = st.text_input("PIN", type="password", max_chars=4)
                goal_name = st.text_input("Goal Name")
                col1, col2 = st.columns(2)
                with col1:
                    target = st.number_input("Target", min_value=1, value=10000)
                with col2:
                    deadline = st.date_input("Deadline", min_value=datetime.now())
                if st.form_submit_button("Create Goal"):
                    success, msg = Bank.add_savings_goal(account_no, pin, goal_name, target,
                                                         deadline.strftime("%Y-%m-%d"))
                    if success:
                        st.success(msg)
                        st.balloons()

    elif "Update" in menu_clean:
        st.markdown("### ✏️ Update Details")
        with st.form("update"):
            col1, col2 = st.columns(2)
            with col1:
                account_no = st.text_input("Account")
            with col2:
                pin = st.text_input("Current PIN", type="password", max_chars=4)
            st.markdown("**Leave empty if no change**")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("New Name")
                email = st.text_input("New Email")
            with col2:
                mobile = st.text_input("New Mobile", max_chars=10)
                new_pin = st.text_input("New PIN", type="password", max_chars=4)
            if st.form_submit_button("Update"):
                success, msg = Bank.update_details(account_no, pin, name or None, email or None,
                                                   mobile or None, None, new_pin or None)
                if success:
                    st.success(msg)

    elif "Delete" in menu_clean:
        st.markdown("### 🗑️ Delete Account")
        st.error("⚠️ WARNING: This is permanent!")
        with st.form("delete"):
            col1, col2 = st.columns(2)
            with col1:
                account_no = st.text_input("Account")
            with col2:
                pin = st.text_input("PIN", type="password", max_chars=4)
            confirm = st.checkbox("I understand this is permanent")
            if st.form_submit_button("Delete"):
                if confirm:
                    success, msg = Bank.delete_account(account_no, pin)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #6c757d;'>
            <p>🏦 Ultimate Bank Management System | © 2025</p>
            <p>✨ Loans | Bills | Goals | Analytics</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()