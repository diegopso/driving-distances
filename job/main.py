import argparse
from dotenv import dotenv_values
from ddmc.pipeline import CheckpointedPipeline
from ddmc.loaders.mysql import MySQL
from ddmc.loaders.csv import CSV

if __name__ == '__main__':
    config = dotenv_values('.env')

    parser = argparse.ArgumentParser(
        prog="Eval driving distances",
        description="Evaluate driving distances of vehicles per day."
    )

    parser.add_argument("-f", "--file", help="A file to be extracted instead of scanning the input directory.", type=str, required=True)
    parser.add_argument("-o", "--output", help="Output path.", type=str, required=True)
    parser.add_argument("-l", "--loader", help="Data loader to be used.", type=str, required=False, default='csv')
    args = parser.parse_args()

    if args.loader == 'mysql':
        loader = MySQL(
            table=config['DB_TABLE'], 
            host_name=config['DB_HOST'], 
            db_name=config['DB_DATABASE'], 
            user=config['DB_USERNAME'], 
            password=config['DB_PASSWORD'],
            touch=args.output
        )
    else:
        loader = CSV(args.output)

    pipeline = CheckpointedPipeline(file=args.file, working_dir=config['WORKING_DIR'], loader=loader)
    pipeline.run()