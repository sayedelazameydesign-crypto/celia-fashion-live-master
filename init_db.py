from app import create_app, db
import os

app = create_app('development')
with app.app_context():
    db.create_all()
    print('Database created successfully!')
