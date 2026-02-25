import os
from pathlib import Path

def view_logs(log_type='all', lines=20):
    """
    View logs from different files
    """
    logs_dir = Path('logs')
    
    if not logs_dir.exists():
        print("No logs directory found. Run fetch_news first!")
        return
    
    log_files = {
        'news': logs_dir / 'news_fetcher.log',
        'errors': logs_dir / 'errors.log',
        'success': logs_dir / 'success.log',
    }
    
    if log_type == 'all':
        for name, path in log_files.items():
            if path.exists():
                print(f"\n{'='*60}")
                print(f"📄 {name.upper()} LOG (last {lines} lines)")
                print('='*60)
                with open(path, 'r') as f:
                    all_lines = f.readlines()
                    for line in all_lines[-lines:]:
                        print(line.strip())
            else:
                print(f"\n{name}.log not found yet")
    else:
        path = log_files.get(log_type)
        if path and path.exists():
            print(f"{log_type.upper()} LOG (last {lines} lines)")
            with open(path, 'r') as f:
                all_lines = f.readlines()
                for line in all_lines[-lines:]:
                    print(line.strip())
        else:
            print(f"Log file not found: {log_type}.log")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        log_type = sys.argv[1]
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        view_logs(log_type, lines)
    else:
        print("   Log Viewer Usage:")
        print("   python view_logs.py [news|errors|success|all] [lines]")
        print("\nExamples:")
        print("   python view_logs.py errors 50    # View last 50 errors")
        print("   python view_logs.py success 30   # View last 30 successes")
        print("   python view_logs.py all 20       # View all logs")