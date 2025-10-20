# 🏦 Ultimate Bank Management System

A complete banking management system built with Python & Streamlit

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.31.0-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🎯 Core Banking Operations
- ➕ **Create Account** - Register with OTP verification
- 💰 **Deposit Money** - Add funds to account
- 💸 **Withdraw Money** - Cash withdrawal with balance check
- 🔄 **Transfer Money** - Send money to other accounts
- 💳 **Virtual Cards** - Auto-generated debit card for each account

### 💼 Advanced Features
- 🏦 **Loan Management** - Personal, Home, Car, Education loans
- 🧮 **EMI Calculator** - Calculate loan repayments before applying
- 💡 **Bill Payments** - Pay electricity, water, gas, mobile, DTH bills
- 👥 **Beneficiary Management** - Save and quick transfer to favorites
- 🎯 **Savings Goals** - Set financial targets and track progress

### 📊 Analytics & Reports
- 📈 **Balance Trends** - Visual chart of account balance over time
- 📊 **Transaction Analysis** - Pie charts and distribution graphs
- 🔍 **Transaction Search** - Filter by date, type, amount
- 📄 **PDF Statements** - Download professional bank statements

### 🎨 UI Features
- 🌙 **Dark Mode Toggle** - Switch between light and dark themes
- 📱 **Responsive Design** - Works on all screen sizes
- 🎨 **Modern Gradients** - Beautiful purple gradient theme
- 📊 **Interactive Charts** - Real-time data visualization

## 🚀 Installation & Setup

### Method 1: Direct Run (Recommended)

1. **Download the project**
   - Click green "Code" button → "Download ZIP"
   - Extract the ZIP file

2. **Install Python**
   - Download from: https://www.python.org/downloads/
   - Version: 3.8 or higher
   - ⚠️ Important: Check "Add Python to PATH" during installation

3. **Install Dependencies**
   ```bash
   # Open Command Prompt/Terminal in project folder
   pip install streamlit pandas plotly reportlab
   ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

5. **Open Browser**
   - Automatically opens at: http://localhost:8501
   - If not, manually visit the URL

### Method 2: Using requirements.txt

```bash
# Navigate to project folder
cd banking-system

# Install all dependencies at once
pip install -r requirements.txt

# Run application
streamlit run app.py
```

## 📖 How to Use

### 1️⃣ Create Account
1. Click "➕ Create" from sidebar
2. Fill details: Name, Age (18+), Email, Mobile, Address, PIN (4 digits)
3. Click "📧 Send OTP"
4. Enter the 6-digit OTP shown on screen
5. Click "✅ Verify & Create"
6. **SAVE YOUR ACCOUNT NUMBER** (e.g., ABCD123456)

### 2️⃣ Deposit Money
1. Select "💰 Deposit" from sidebar
2. Enter Account Number and PIN
3. Enter amount (Max: ₹50,000 per transaction)
4. Click "💰 Deposit"

### 3️⃣ Transfer Money
1. Select "🔄 Transfer" from sidebar
2. Enter your Account Number and PIN
3. Enter recipient's Account Number
4. Enter amount (Max: ₹1,00,000 per transaction)
5. Add description (optional)
6. Click "🔄 Transfer"

### 4️⃣ Apply for Loan
1. Go to "💳 Loans" section
2. Select "Apply Loan" tab
3. Choose loan type (Personal/Home/Car/Education)
4. Enter amount, tenure, and purpose
5. Click "🎯 Apply"
6. Loan approved instantly!
7. Amount credited to account immediately

### 5️⃣ Pay Bills
1. Go to "💡 Bill Payment"
2. Enter Account Number and PIN
3. Select bill type
4. Enter provider name and bill number
5. Enter amount
6. Click "💳 Pay Bill"

### 6️⃣ Set Savings Goal
1. Go to "🎯 Goals" section
2. Click "Add Goal" tab
3. Enter goal name (e.g., "New Phone")
4. Set target amount and deadline
5. Click "Create Goal"
6. Contribute anytime from "View Goals" tab

## 🎯 Key Features Explained

### 🔒 Security
- **PIN Protection**: All PINs stored as SHA-256 hash
- **OTP Verification**: 6-digit OTP with 5-minute validity
- **Input Validation**: All inputs checked for security
- **Transaction Limits**: Prevents fraud with maximum limits

### 💳 Loan System
- **Interest Rates**:
  - Personal Loan: 12.5% p.a.
  - Home Loan: 8.5% p.a.
  - Car Loan: 10.0% p.a.
  - Education Loan: 9.0% p.a.
- **EMI Calculator**: Calculate before applying
- **Instant Approval**: No waiting time
- **Flexible Repayment**: Pay EMI monthly or close loan anytime

### 👥 Beneficiary System
- Save frequently used accounts
- Add custom nicknames (e.g., "Mom", "Brother")
- Quick transfer with one click
- Remove beneficiary anytime

### 📊 Analytics
- **Balance Trend**: Line chart showing balance over time
- **Transaction Distribution**: Pie chart of transaction types
- **Transaction History**: Complete record with filters
- **PDF Statements**: Professional downloadable reports

## 🛠️ Technology Used

| Technology | Purpose |
|------------|---------|
| Python 3.8+ | Programming Language |
| Streamlit | Web Framework |
| Pandas | Data Processing |
| Plotly | Interactive Charts |
| ReportLab | PDF Generation |
| JSON | Data Storage |
| Hashlib | Password Security |

## 📂 Project Structure

```
banking-system/
│
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── data.json          # Database (auto-created)
└── .gitignore         # Git ignore rules
```

## 🎓 Sample Test Account

Create your first account with these details:
- Name: Test User
- Age: 25
- Email: test@example.com
- Mobile: 9876543210
- PIN: 1234

Then you'll receive your Account Number!

## 📸 Screenshots

### Home Dashboard
Shows total accounts, balance, and transactions

### Account Creation
OTP verification system with countdown timer

### Transaction Dashboard
View balance, recent transactions, and analytics

### Loan Management
Apply loans, view EMI schedule, make payments

### Bill Payment
Pay utility bills directly from account

## ⚙️ Configuration

### Transaction Limits
- Deposit: ₹50,000 per transaction
- Transfer: ₹1,00,000 per transaction
- Loan: ₹10,000 to ₹50,00,000

### OTP Settings
- Validity: 5 minutes
- Length: 6 digits
- Auto-expires after time limit

## 🐛 Troubleshooting

### Issue: Streamlit not found
```bash
Solution: pip install streamlit
```

### Issue: Module not found error
```bash
Solution: pip install -r requirements.txt
```

### Issue: Port already in use
```bash
Solution: streamlit run app.py --server.port 8502
```

### Issue: Data file corrupted
```bash
Solution: Delete data.json and restart app
```

## 🔄 Future Enhancements

- [ ] Multi-currency support
- [ ] Interest on savings account
- [ ] Fixed deposit schemes
- [ ] Cheque book management
- [ ] Transaction notifications
- [ ] Mobile app version
- [ ] Multi-language support
- [ ] Biometric authentication

## 🤝 Contributing

Want to improve this project? Here's how:

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Created with ❤️ for learning purposes

**Your Name**
- GitHub: @yourusername
- Email: your.email@example.com

## 🙏 Acknowledgments

- Thanks to Streamlit for amazing framework
- Plotly for beautiful charts
- Python community for great libraries

## 📞 Support & Contact

- **Issues**: Create an issue on GitHub
- **Email**: your.email@example.com
- **Documentation**: Read this README

## ⭐ Star This Repo

If you like this project, give it a ⭐ on GitHub!

---

**Made with 🏦 Python | Streamlit | Plotly**

*Last Updated: January 2025*