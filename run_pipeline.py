#from src.pipeline import run_all

#if __name__ == "__main__":
#    run_all()


import argparse
from src.pipeline import run_all

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", default=None)
    parser.add_argument("--end-date", default=None)
    args = parser.parse_args()

    run_all(start_date=args.start_date, end_date=args.end_date)