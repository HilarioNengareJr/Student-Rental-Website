import os
import logging
import threading

from app import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _truthy(value: str) -> bool:
    return str(value).lower() in ('1', 'true', 'yes', 'on')


def start_scraper_threads() -> None:
    '''Launch the background scrapers in daemon threads.

    Gated behind ENABLE_SCRAPER_THREADS and only ever called from the dev-server
    entrypoint below (never under Gunicorn). Imports are lazy so the app boots
    without Selenium/Chrome installed, and each scraper is failure-isolated so a
    crash or hang in one never brings down the web app.
    '''
    def _run(label, module_name, func_name):
        try:
            module = __import__(module_name, fromlist=[func_name])
            getattr(module, func_name)()
        except Exception as exc:
            logger.exception('Scraper "%s" failed: %s', label, exc)

    for label, module_name, func_name in (
        ('estate', 'app.webspider.estate_scraper', 'background_task'),
        ('blog', 'app.webspider.blog_scraper', 'run_background_task'),
    ):
        threading.Thread(target=_run, args=(label, module_name, func_name), daemon=True).start()


if __name__ == '__main__':
    if _truthy(os.getenv('ENABLE_SCRAPER_THREADS', 'false')):
        logger.info('ENABLE_SCRAPER_THREADS is set — launching background scrapers')
        start_scraper_threads()

    app.run(debug=_truthy(os.getenv('FLASK_DEBUG', 'false')), host='0.0.0.0', port=5000)
