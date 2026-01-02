"""
File Watcher - Auto-trigger pipeline when new files are added
"""

import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
# Import from current package
from .pipeline import run_pipeline

# Setup logging
BASE_DIR = Path(__file__).parent.parent
log_dir = BASE_DIR / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'watcher.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class DataFolderHandler(FileSystemEventHandler):
    """Handle file system events in the data folder"""
    
    def __init__(self, cooldown=30):
        self.cooldown = cooldown  # seconds to wait before triggering
        self.last_trigger = 0
        
    def on_created(self, event):
        """Triggered when a new file is created"""
        if event.is_directory:
            return
        
        # Only process Excel files
        if event.src_path.endswith('.xlsx'):
            current_time = time.time()
            
            # Check cooldown period
            if current_time - self.last_trigger > self.cooldown:
                logging.info(f"📁 New file detected: {Path(event.src_path).name}")
                logging.info("🚀 Triggering pipeline...")
                
                try:
                    run_pipeline(archive=True)
                    self.last_trigger = current_time
                except Exception as e:
                    logging.error(f"❌ Pipeline failed: {str(e)}")
            else:
                logging.info(f"⏳ Cooldown active, skipping trigger for {Path(event.src_path).name}")

def start_watcher(folder_path='data', cooldown=30):
    """Start watching the data folder"""
    # Get absolute path relative to project root
    if not Path(folder_path).is_absolute():
        path = BASE_DIR / folder_path
    else:
        path = Path(folder_path)
    
    if not path.exists():
        path.mkdir(parents=True)
        logging.info(f"📁 Created data folder: {path}")
    
    event_handler = DataFolderHandler(cooldown=cooldown)
    observer = Observer()
    observer.schedule(event_handler, str(path), recursive=False)
    observer.start()
    
    logging.info("=" * 70)
    logging.info(f"👁️ Watching folder: {path.absolute()}")
    logging.info(f"⏱️ Cooldown period: {cooldown} seconds")
    logging.info("🔄 Add .xlsx files to trigger the pipeline automatically")
    logging.info("Press Ctrl+C to stop")
    logging.info("=" * 70)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("⏹️ Watcher stopped by user")
    
    observer.join()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='File Watcher for Auto Pipeline')
    parser.add_argument('--folder', default='data', help='Folder to watch')
    parser.add_argument('--cooldown', type=int, default=30, help='Cooldown in seconds')
    
    args = parser.parse_args()
    start_watcher(folder_path=args.folder, cooldown=args.cooldown)
