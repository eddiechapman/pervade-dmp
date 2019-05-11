import csv
import os
from time import time

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Award



FILENAME = '/home/eddie/Projects/PERVADE/pervade-dmp/pervade_dmp_awards.csv'
FIELDNAMES = (
    'pi_name',
    'contact',
    'pi_email',
    'organization',
    'program',
    'title',
    'abstract',
    'award_number',
    'id'
)


if __name__ == "__main__":
    t = time()

    Base = declarative_base()
    # Create the database
    #basedir = os.path.abspath(os.path.dirname(__file__))
    #engine = create_engine('sqlite:///' + os.path.join(basedir, 'app.db'))
    engine = create_engine('')


    Session = sessionmaker(bind=engine)
    session = Session()
    
    Base.metadata.create_all(bind=engine)

    try:
        with open(FILENAME, 'r', encoding='UTF-8') as csvfile:
            reader = csv.DictReader(csvfile, FIELDNAMES)
            for i, row in enumerate(reader):
                record = Award(**{
                    'pi_name': row['pi_name'],
                    'contact': row['contact'],
                    'pi_email': row['pi_email'],
                    'organization': row['organization'],
                    'program': row['program'],
                    'title': row['title'],
                    'abstract': row['abstract'],
                    'award_id': row['award_number']
                    })
                session.add(record)
                if i % 1000 == 0:
                    session.flush()
                    print('*flush*')
            session.commit()
            print('we did it')
    except Exception as e:
        session.rollback()
        print(e)
    finally:
        session.close()
    print("Time elapsed: " + str(time() - t) + " s.")
