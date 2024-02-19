from app import app
from app.webspider.estate_scraper import background_task
from app.webspider.blog_scraper import run_background_task
import threading

"""
def start_background_task():
    background_task_thread = threading.Thread(target=background_task)
    background_task_thread.start()

def start_run_background_task():
    run_background_thread = threading.Thread(target=run_background_task)
    run_background_thread.start()
    
start_background_task()
start_run_background_task()
"""

if __name__ == '__main__':
    
    
    app.run(debug=True, host='0.0.0.0', port=5000)
