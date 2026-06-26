"""Simulate what Render runs to find the real error."""
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['FLASK_ENV'] = 'production'
os.environ['FIREBASE_CREDENTIALS_PATH'] = './firebase-credentials.json'

try:
    from backend.app import create_app
    app = create_app('production')
    
    with app.test_client() as client:
        resp = client.post('/api/analyze/text', json={
            'text': 'Breaking news Scientists discover water on Mars confirming decades of speculation about the red planet. NASA announced the findings at a press conference today and confirmed the discovery.',
            'title': 'Test'
        })
        print('STATUS:', resp.status_code)
        print('BODY:', resp.get_data(as_text=True)[:2000])
except Exception as e:
    print('CRASH:', type(e).__name__, str(e))
    traceback.print_exc()
