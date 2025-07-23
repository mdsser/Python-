from flask import Flask, render_template, request, redirect, url_for, flash
from models import init_db, Script
from utils import execute_script
import os
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'scripts'

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scripts')
def script_list():
    engine = create_engine('sqlite:///ops.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    scripts = session.query(Script).all()
    session.close()
    return render_template('script_list.html', scripts=scripts)

@app.route('/scripts/<int:script_id>')
def script_detail(script_id):
    engine = create_engine('sqlite:///ops.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    script = session.query(Script).filter(Script.id == script_id).first()
    session.close()
    return render_template('script_detail.html', script=script)

@app.route('/scripts/upload', methods=['GET', 'POST'])
def upload_script():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            script = Script(name=filename, path=file_path)
            engine = create_engine('sqlite:///ops.db')
            Session = sessionmaker(bind=engine)
            session = Session()
            session.add(script)
            session.commit()
            session.close()
            flash('Script uploaded successfully!')
            return redirect(url_for('script_list'))
    return render_template('upload.html')

@app.route('/scripts/execute/<int:script_id>')
def execute_script_route(script_id):
    engine = create_engine('sqlite:///ops.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    script = session.query(Script).filter(Script.id == script_id).first()
    if script:
        result = execute_script(script.path)
        session.close()
        return render_template('script_detail.html', script=script, result=result)
    session.close()
    flash('Script not found!')
    return redirect(url_for('script_list'))

if __name__ == '__main__':
    app.run(debug=True)
