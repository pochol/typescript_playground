"""Wysłka zdjęcia + analizy do Firebase (Storage + Firestore).

Dashboard React czyta z tych samych kolekcji/bucketu.
"""
from __future__ import annotations

import os
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore, storage


class Uploader:
    def __init__(self, bucket: Optional[str] = None):
        bucket = bucket or os.environ["FIREBASE_STORAGE_BUCKET"]
        if not firebase_admin._apps:
            # Poświadczenia z GOOGLE_APPLICATION_CREDENTIALS (service account JSON).
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {"storageBucket": bucket})
        self.bucket = storage.bucket()
        self.db = firestore.client()

    def upload(self, local_path: str, doc_id: str, captured_at_ms: int,
               analysis: Optional[dict]) -> str:
        """Wgrywa plik do Storage i zapisuje dokument w Firestore.

        Zwraca publiczny URL zdjęcia.
        """
        blob = self.bucket.blob(f"growkit/{doc_id}.jpg")
        blob.upload_from_filename(local_path, content_type="image/jpeg")
        blob.make_public()
        url = blob.public_url

        doc = {
            "id": doc_id,
            "imageUrl": url,
            "capturedAt": captured_at_ms,
            "analysis": analysis,           # None jeśli AI wyłączone
            "createdAt": firestore.SERVER_TIMESTAMP,
        }
        self.db.collection("growkit_photos").document(doc_id).set(doc)
        return url
