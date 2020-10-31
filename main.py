from backend.crawler import find_mails
from backend.log import logger

OUTPUT_FILE = "output.txt"

if __name__ == '__main__':
    # finding mails
    mails = find_mails("ingegneria")

    # writing to file
    with open(OUTPUT_FILE, 'w+') as fout:
        print(*mails, sep="\n", file=fout)

    logger.info(f"All data written to: {OUTPUT_FILE}")
