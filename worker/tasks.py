import logging

from worker.celery_app import celery_app
from worker.utils import extract_metadata, download_audio
from models.song import save_song

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def download_task(self, url, labels):
    logger.info("Task %s started: url=%s labels=%s", self.request.id, url, labels)
    try:
        metadata = extract_metadata(url)
        logger.info("Task %s: metadata extracted – title=%s", self.request.id, metadata.get("title"))

        file_path = download_audio(url)
        logger.info("Task %s: audio downloaded to %s", self.request.id, file_path)

        save_song(metadata, labels, file_path)
        logger.info("Task %s: song saved to database", self.request.id)

        return {"status": "done"}
    except Exception as exc:
        logger.exception("Task %s failed: %s", self.request.id, exc)
        return {"status": "error", "detail": "Download failed. Check worker logs for details."}
