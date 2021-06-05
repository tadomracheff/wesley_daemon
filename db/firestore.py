import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from db.postgres import get_location
import threading


def listen():
    cred = credentials.Certificate('config/serviceAccount.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    callback_done = threading.Event()

    def on_snapshot(doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            location = doc.to_dict()
            segment_id = get_location(location["lat"], location["lng"])
            print(doc.id)
            print('segment_id =', segment_id)
        callback_done.set()
        print('---')

    doc_ref = db.collection("location")

    doc_watch = doc_ref.on_snapshot(on_snapshot)
