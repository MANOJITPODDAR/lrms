from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_from_directory
import sqlite3, os
from datetime import date
from functools import wraps

app = Flask(__name__)
app.secret_key = 'lrms_andaman_2026_secret_key_x9z'
DB_PATH = os.path.join(os.path.dirname(__file__), 'lrms.db')

DEFAULT_PASSWORDS = {
    'masteradmin': 'Ma$t3r@2026',
    'wandoor':      'Wn7kR2mP',
    'manpur':       'Mp4xJ9qL',
    'ferrargunj':   'Fg2nT8vY',
    'wimberlygunj': 'Wg6bK3sX',
    'kadamtala':    'Kt9pM5zQ',
    'bakultala':    'Bt3hN7wR',
    'rangat':       'Rg8cF2jV',
    'billiground':  'Bg5yD4nK',
    'diglipur':     'Dp7mX3qT',
    'vijaynagar':   'Vn2kL9bS',
    'campbellbay':  'Cb6rP4hM',
    'kamorta':      'Km9wZ2vJ',
    'katchal':      'Kc4tG8xN',
    'hutbay':       'Hb3sQ7mF',
    'rkpur':        'Rk6pY2nC',
    'swarajdweep':  'Sd8xB5kT',
    'shaheed':      'Sh4vM9qL',
    'longisland':   'Li7jN3rW',
}

LIBRARIES = [
    (1,  'Zonal Library Wandoor',      'wandoor'),
    (2,  'Zonal Library Manpur',       'manpur'),
    (3,  'Zonal Library Ferrargunj',   'ferrargunj'),
    (4,  'Zonal Library Wimberlygunj', 'wimberlygunj'),
    (5,  'Zonal Library Kadamtala',    'kadamtala'),
    (6,  'Zonal Library Bakultala',    'bakultala'),
    (7,  'Zonal Library Rangat',       'rangat'),
    (8,  'Zonal Library Billiground',  'billiground'),
    (9,  'Zonal Library Diglipur',     'diglipur'),
    (10, 'Zonal Library Vijay Nagar',  'vijaynagar'),
    (11, 'Zonal Library Campbell Bay', 'campbellbay'),
    (12, 'Zonal Library Kamorta',      'kamorta'),
    (13, 'Zonal Library Katchal',      'katchal'),
    (14, 'Zonal Library Hutbay',       'hutbay'),
    (15, 'Zonal Library R K Pur',      'rkpur'),
    (16, 'Zonal Library Swaraj Dweep', 'swarajdweep'),
    (17, 'Zonal Library Shaheed Dweep','shaheed'),
    (18, 'Zonal Library Long Island',  'longisland'),
]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS libraries (
        id INTEGER PRIMARY KEY, name TEXT NOT NULL, username TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, password TEXT NOT NULL,
        role TEXT NOT NULL, library_id INTEGER, display TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        library_id INTEGER NOT NULL, membership_card_number TEXT,
        request_date DATE NOT NULL, requested_item_type TEXT NOT NULL,
        requested_item_subtype TEXT, requested_item_name TEXT NOT NULL,
        other_description TEXT, submitted_by TEXT DEFAULT 'staff',
        FOREIGN KEY (library_id) REFERENCES libraries(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        library_id INTEGER NOT NULL,
        reader_name TEXT, contact_number TEXT, gender TEXT, age INTEGER,
        occupation TEXT, visit_frequency TEXT, visit_purpose TEXT,
        subjects_preferred TEXT, preferred_language TEXT, preferred_format TEXT,
        materials_adequate TEXT, suggestions TEXT,
        staff_assistance TEXT, staff_issues TEXT, ambiance_satisfactory TEXT,
        submission_date DATE NOT NULL,
        FOREIGN KEY (library_id) REFERENCES libraries(id))''')

    c.execute('SELECT COUNT(*) FROM libraries')
    if c.fetchone()[0] == 0:
        c.executemany('INSERT INTO libraries (id,name,username) VALUES (?,?,?)', LIBRARIES)

    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users VALUES ('masteradmin',?,'master',NULL,'Master Administrator')",
                  (DEFAULT_PASSWORDS['masteradmin'],))
        for lid, lname, uname in LIBRARIES:
            c.execute("INSERT INTO users VALUES (?,?,'admin',?,?)",
                      (uname, DEFAULT_PASSWORDS[uname], lid, lname))
    conn.commit()
    conn.close()

def login_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if 'username' not in session:
            return redirect(url_for('login_page'))
        return f(*a, **kw)
    return dec

def master_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if session.get('role') != 'master':
            return jsonify({'error': 'Unauthorized'}), 403
        return f(*a, **kw)
    return dec

# ── PAGES ──────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('visitor_page') if session.get('role') == 'guest' else url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('login.html', libraries=[(r[0], r[1]) for r in LIBRARIES])

@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('role') == 'guest':
        return redirect(url_for('visitor_page'))
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username=?', (session['username'],)).fetchone()
    conn.close()
    return render_template('dashboard.html',
        username=session['username'], display=user['display'],
        role=user['role'], library_id=user['library_id'],
        libraries=[(r[0], r[1]) for r in LIBRARIES])

@app.route('/visitor')
@login_required
def visitor_page():
    if session.get('role') != 'guest':
        return redirect(url_for('dashboard'))
    lib_id   = session.get('library_id')
    lib_name = next((r[1] for r in LIBRARIES if r[0] == lib_id), 'Library')
    return render_template('visitor.html',
        library_id=lib_id, library_name=lib_name,
        libraries=[(r[0], r[1]) for r in LIBRARIES])

@app.route('/report')
@login_required
def report_page():
    if session.get('role') == 'guest':
        return redirect(url_for('visitor_page'))
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username=?', (session['username'],)).fetchone()
    conn.close()
    return render_template('report.html',
        username=session['username'], display=user['display'],
        role=user['role'], library_id=user['library_id'],
        libraries=[(r[0], r[1]) for r in LIBRARIES])

@app.route('/static/logo.png')
def serve_logo():
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'), 'logo.png')

# ── AUTH API ───────────────────────────────────────────────────────────────────
@app.route('/api/login', methods=['POST'])
def api_login():
    data   = request.get_json()
    utype  = data.get('user_type', 'staff')
    if utype == 'guest':
        lib_id = data.get('library_id')
        if not lib_id:
            return jsonify({'success': False, 'error': 'Please select a library'}), 400
        lib_name = next((r[1] for r in LIBRARIES if r[0] == int(lib_id)), None)
        if not lib_name:
            return jsonify({'success': False, 'error': 'Invalid library'}), 400
        session.update({'username': 'guest', 'role': 'guest',
                        'library_id': int(lib_id), 'display': f'Visitor — {lib_name}'})
        return jsonify({'success': True, 'role': 'guest', 'display': session['display']})

    username = data.get('username', '').strip().lower()
    password = data.get('password', '').strip()
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
    conn.close()
    if user and user['password'] == password:
        session.update({'username': username, 'role': user['role'],
                        'library_id': user['library_id'], 'display': user['display']})
        return jsonify({'success': True, 'role': user['role'], 'display': user['display']})
    return jsonify({'success': False, 'error': 'Invalid username or password'}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

# ── PASSWORD MANAGEMENT ────────────────────────────────────────────────────────
@app.route('/api/users', methods=['GET'])
@login_required
@master_required
def get_users():
    conn = get_db()
    rows = conn.execute("SELECT username, password, display FROM users WHERE role='admin' ORDER BY display").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/users/change-password', methods=['POST'])
@login_required
@master_required
def change_password():
    data    = request.get_json()
    target  = data.get('username')
    new_pw  = data.get('new_password', '').strip()
    if not target or not new_pw:
        return jsonify({'error': 'Missing fields'}), 400
    if len(new_pw) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    conn = get_db()
    conn.execute("UPDATE users SET password=? WHERE username=? AND role='admin'", (new_pw, target))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ── LIBRARIES ──────────────────────────────────────────────────────────────────
@app.route('/api/libraries')
@login_required
def api_libraries():
    role   = session.get('role')
    lib_id = session.get('library_id')
    if role in ('master', 'guest'):
        return jsonify([{'id': r[0], 'name': r[1]} for r in LIBRARIES])
    lib = next((r for r in LIBRARIES if r[0] == lib_id), None)
    return jsonify([{'id': lib[0], 'name': lib[1]}] if lib else [])

# ── REQUESTS ───────────────────────────────────────────────────────────────────
@app.route('/api/requests', methods=['POST'])
@login_required
def create_request():
    data = request.get_json()
    role = session.get('role')
    if role in ('admin', 'guest'):
        library_id = session.get('library_id')
    else:
        library_id = data.get('library_id')
    submitted_by = 'guest' if role == 'guest' else 'staff'
    membership = data.get('membership_card_number') or None
    item_type  = data.get('requested_item_type')
    item_sub   = data.get('requested_item_subtype') or None
    item_name  = (data.get('requested_item_name') or '').strip()
    other_desc = data.get('other_description') or None
    if not library_id or not item_type or not item_name:
        return jsonify({'error': 'Missing required fields'}), 400
    conn = get_db()
    conn.execute('''INSERT INTO requests (library_id, membership_card_number, request_date,
        requested_item_type, requested_item_subtype, requested_item_name, other_description, submitted_by)
        VALUES (?,?,?,?,?,?,?,?)''',
        (library_id, membership, date.today().isoformat(), item_type, item_sub, item_name, other_desc, submitted_by))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Request submitted successfully'}), 201

# ── FEEDBACK ───────────────────────────────────────────────────────────────────
@app.route('/api/feedback', methods=['POST'])
@login_required
def submit_feedback():
    if session.get('role') != 'guest':
        return jsonify({'error': 'Only visitors can submit feedback'}), 403
    data   = request.get_json()
    lib_id = session.get('library_id')
    conn = get_db()
    conn.execute('''INSERT INTO feedback
        (library_id, reader_name, contact_number, gender, age, occupation,
         visit_frequency, visit_purpose, subjects_preferred, preferred_language,
         preferred_format, materials_adequate, suggestions, staff_assistance,
         staff_issues, ambiance_satisfactory, submission_date)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
        lib_id,
        data.get('reader_name') or None,       data.get('contact_number') or None,
        data.get('gender') or None,             data.get('age') or None,
        data.get('occupation') or None,         data.get('visit_frequency') or None,
        data.get('visit_purpose') or None,      data.get('subjects_preferred') or None,
        data.get('preferred_language') or None, data.get('preferred_format') or None,
        data.get('materials_adequate') or None, data.get('suggestions') or None,
        data.get('staff_assistance') or None,   data.get('staff_issues') or None,
        data.get('ambiance_satisfactory') or None, date.today().isoformat()
    ))
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 201

# ── REPORTS ────────────────────────────────────────────────────────────────────
@app.route('/api/reports/all')
@login_required
def report_all():
    role      = session.get('role')
    lib_sess  = session.get('library_id')
    start     = request.args.get('start_date')
    end       = request.args.get('end_date')
    lib_filt  = request.args.get('library_id', 'all')
    q = '''SELECT r.id, l.name as library_name, r.membership_card_number,
           r.request_date, r.requested_item_type, r.requested_item_subtype,
           r.requested_item_name, r.other_description, r.submitted_by
           FROM requests r JOIN libraries l ON r.library_id=l.id WHERE 1=1'''
    p = []
    if role != 'master':
        q += ' AND r.library_id=?'; p.append(lib_sess)
    elif lib_filt != 'all':
        q += ' AND r.library_id=?'; p.append(lib_filt)
    if start: q += ' AND r.request_date>=?'; p.append(start)
    if end:   q += ' AND r.request_date<=?'; p.append(end)
    q += ' ORDER BY r.request_date DESC, r.id DESC'
    conn = get_db()
    rows = conn.execute(q, p).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/reports/popular')
@login_required
def report_popular():
    role     = session.get('role')
    lib_sess = session.get('library_id')
    start    = request.args.get('start_date')
    end      = request.args.get('end_date')
    lib_filt = request.args.get('library_id', 'all')
    q = 'SELECT requested_item_name, requested_item_type, COUNT(*) as count FROM requests WHERE 1=1'
    p = []
    if role != 'master':
        q += ' AND library_id=?'; p.append(lib_sess)
    elif lib_filt != 'all':
        q += ' AND library_id=?'; p.append(lib_filt)
    if start: q += ' AND request_date>=?'; p.append(start)
    if end:   q += ' AND request_date<=?'; p.append(end)
    q += ' GROUP BY requested_item_name ORDER BY count DESC LIMIT 10'
    conn = get_db()
    rows = conn.execute(q, p).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/reports/summary')
@login_required
def report_summary():
    role     = session.get('role')
    lib_sess = session.get('library_id')
    start    = request.args.get('start_date')
    end      = request.args.get('end_date')
    lib_filt = request.args.get('library_id', 'all')
    base = 'FROM requests r WHERE 1=1'
    p = []
    if role != 'master':
        base += ' AND r.library_id=?'; p.append(lib_sess)
    elif lib_filt != 'all':
        base += ' AND r.library_id=?'; p.append(lib_filt)
    if start: base += ' AND r.request_date>=?'; p.append(start)
    if end:   base += ' AND r.request_date<=?'; p.append(end)
    conn = get_db()
    total   = conn.execute(f'SELECT COUNT(*) as c {base}', p).fetchone()['c']
    by_type = conn.execute(f'SELECT requested_item_type, COUNT(*) as c {base} GROUP BY requested_item_type', p).fetchall()
    conn.close()
    return jsonify({'total': total, 'by_type': [dict(r) for r in by_type]})

@app.route('/api/reports/feedback')
@login_required
@master_required
def report_feedback():
    start    = request.args.get('start_date')
    end      = request.args.get('end_date')
    lib_filt = request.args.get('library_id', 'all')
    q = 'SELECT f.*, l.name as library_name FROM feedback f JOIN libraries l ON f.library_id=l.id WHERE 1=1'
    p = []
    if lib_filt != 'all':
        q += ' AND f.library_id=?'; p.append(lib_filt)
    if start: q += ' AND f.submission_date>=?'; p.append(start)
    if end:   q += ' AND f.submission_date<=?'; p.append(end)
    q += ' ORDER BY f.submission_date DESC, f.id DESC'
    conn = get_db()
    rows = conn.execute(q, p).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
