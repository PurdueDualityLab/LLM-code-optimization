import subprocess
import sys
from collections import Counter
from dotenv import load_dotenv
from utils import Logger
import os

load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')
logger = Logger("logs", sys.argv[2]).logger

def get_hotspots(application_name, top_K):
    """Run the Java application with async-profiler. Need to manually run ant build command first."""
    try:        
        logger.info("Running application {application_name} with async-profiler...")
        profiler_cmd = [
            "java",
            f"-agentpath:{USER_PREFIX}/async-profiler/build/lib/libasyncProfiler.so=start,event=cpu,file=profile.txt,collapsed",
            "-jar", "/home/hpeng/E2COOL/benchmark_dacapo/benchmarks/dacapo-evaluation-git-unknown${git.dirty}.jar", application_name
        ]
        subprocess.run(profiler_cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during async-profiler execution: {e}")

    hotspots = extract_hotspots(application_name, top_K)
    return hotspots

def extract_hotspots(filter_term, top_K):
    ignore = [
            "org/apache/fop/fo/FOTreeBuilder$3.run",
            "org/apache/fop/cli/Main.startFOP",
        ]

    try:
        with open("profile.txt", 'r') as file:
            data = file.readlines()
        
        methods = Counter()
        
        for line in data:
            if line:
                methods_in_line = line.split(';')
                for method in methods_in_line:
                    if method in ignore:
                        continue
                    if filter_term in method:
                        methods[method] += 1
        
        logger.info("Top CPU Hotspots:")
        hotspots_dict = {method: count for method, count in methods.most_common(top_K)}
        logger.info(hotspots_dict)
        return hotspots_dict
    except FileNotFoundError:
        logger.error("Error: profile.txt not found.")