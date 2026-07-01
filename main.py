from pipeline.collector import Collector
from pipeline.monitor import Monitor

def start_pipeline():
    collector = Collector()
    monitor = Monitor()
    print("Collection of Messenger is Started")
    messenger = collector.collect_messenger()
    print("Collection of Messenger is Completer")
    print("Collection of Instagram is Started")
    insta = collector.collect_instagram()
    print("Collector for Instagram is completed")
    print("Started the Monitoring of the New Messages in both Instagram and Facebook Concurrently")
    monitor.start_all()

if __name__ == "__main__":
    print("Started the Pipeline")
    start_pipeline()
