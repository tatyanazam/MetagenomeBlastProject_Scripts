#!/usr/bin/env python3

import argparse
import hashlib
import logging
import os
import os.path
import pathlib
import requests
import sys
import time
from bs4 import BeautifulSoup as bs
from http.cookiejar import MozillaCookieJar
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

__version = 190708.1
# CONFIGURATION
DEBUG = False
VERBOSE = False
base_url = "https://genome.jgi.doe.gov"
headers = {'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'} 
max_retries = 100
timeout = 60.0
sleep = 60
 
def setup_logger(name=None, logfile=None, debug=False):
    """
    Set up logging to a file or stdout
    Arguments:
    * logfile - file to write logs to
    * log level - verbose or debug
    """
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    if not name:
        name = __name__
    log = logging.getLogger(name)
    if logfile:
        file_log = logging.FileHandler(logfile)
        file_log.setFormatter(formatter)
        log.addHandler(file_log)
    console_log = logging.StreamHandler(stream=sys.stdout)
    console_log.setFormatter(formatter)
    if debug:
        console_log.setLevel(logging.DEBUG)
        log.setLevel("DEBUG")
    else:
        console_log.setLevel(logging.INFO)
        log.setLevel("INFO")
    log.addHandler(console_log)
    return log


def parse_args(print_help=False):
    """Parse command-line arguments"""
    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write("error: %s\n" % message)
            self.print_help()
            sys.exit(2)

    parser = MyParser(
        usage="%(prog)s [options] <filenames>",
        description="""Download JGI datasets from URIs parsed out of xml files."""
    )
    parser.add_argument(
        "--version",
        action="version",
        version="""%(prog)s
                        Version: {version}""".format(
            version=__version
        ),
    )
    parser.add_argument(
        "--minsize",
        type=int,
        default=1024,
        help="Minimal fasta file size (default: 1kb)",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        default=os.getenv('OUTDIR') or 'Assembled_fasta_files',
        help="output directory",
    )
    parser.add_argument(
        "-r",
        "--retries",
        dest="max_retries",
        type=int,
        default=100,
        help="max retries (default: 100)",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        dest="timeout",
        type=int,
        default=60.0,
        help="web timeout (default: 60sec)",
    )
    parser.add_argument(
        "-s",
        "--sleep",
        dest="sleep",
        type=int,
        default=60,
        help="sleep between retries (default: 60sec)",
    )
    parser.add_argument(
        "-p", "--parseonly", action="store_true", default=False, help="Only parse for links. Do not download.",
    )
    parser.add_argument(
        "--tagfilename", action="store_true", default=False, help="Prepend input filename to output file name for troubleshooting.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="Verbose output",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", default=False, help="Turn on debugging output",
    )
    parser.add_argument(
        "infiles",
        type=str,
        nargs='+',
    )
    if print_help:
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args()
    return args



def md5(fname):
    log = logging.getLogger()
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    if DEBUG:
        log.debug(f"File / hash: {fname} / {hash_md5.hexdigest()}")
    return hash_md5.hexdigest()


def get_cookies():
    """Get cookies from the cookies.txt file after a login"""
    log = logging.getLogger()
    cj = MozillaCookieJar()
    cj.load('cookies.txt', ignore_discard=True, ignore_expires=True)
    for cookie in cj:
        cookie.expires = time.time() + 14 * 24 * 3600
    if DEBUG:
        log.debug(f"Cookiejar: {cj}")
        log.debug(f"Cookiejar length: {len(cj)}")
    return cj


def download_records(args, records, cj):
    """Download records from one input file"""
    log = logging.getLogger()
    for rec in records:
        if DEBUG:
            log.debug(f"Record:\n{rec}")
        md5_match = False
        rec_label = records[rec]['label'].replace(" ", "_")
        rec_label = rec_label.replace("/", "_")
        rec_url = records[rec]['url']
        in_file_path = pathlib.Path(args.in_filename).stem
        noblock_url = rec_url.replace("blocking=true", "blocking=false")
        rec_filename = records[rec]['filename']
        if args.tagfilename:
            out_fname = f"{args.outdir}/{in_file_path}-{rec_label}_{rec_filename}"
        else:
            out_fname = f"{args.outdir}/{rec_label}_{rec_filename}"
        rec_md5 = records[rec]['md5']
        wget_url = f"{base_url}{noblock_url}"
        if os.path.isfile(out_fname):
            if md5(out_fname) == rec_md5:
                if VERBOSE:
                    log.info(f"File '{out_fname}' already exists and md5 sums match, skipping.")
                continue
            else:
                if VERBOSE:
                    log.info(f"File '{out_fname}' exists, but md5 sums do not match. Deleting and re-downloading.")
                os.unlink(out_fname)
        if 'sizeinbytes' in records[rec]:
            size_label = 'sizeinbytes'
        else:
            size_label = 'sizeInBytes'
        if int(records[rec][size_label]) <= args.minsize:
            log.info("Skipping '{rec}', smaller than '{minsize}' size")
            continue
        if VERBOSE:
            log.info(f"Downloading '{rec_filename}' from '{wget_url}' to {out_fname}")
        session = requests.Session()
        retry_counter = 0
        retries = Retry(total=args.max_retries, backoff_factor=0.1) 
        session.mount('http://', HTTPAdapter(max_retries=retries))
        while retry_counter < args.max_retries:
            r = requests.get(wget_url, headers = headers, cookies = cj, stream = True, timeout=args.timeout)
            with open(out_fname, "wb") as outfile:
                for chunk in r.iter_content(chunk_size = 1024):
                    if chunk:
                        outfile.write(chunk)
            out_md5 = md5(out_fname)
            if DEBUG:
                log.debug(f"JGI checksum for {out_fname}: {rec_md5}")
                log.debug(f"File checksum for {out_fname}: {out_md5}")
            if rec_md5 == out_md5:
                if VERBOSE:
                    log.info(f"Checksums match, {out_fname} download finished.")
                break
            else:
                if VERBOSE:
                    log.warn(f"Attempt {retry_counter+1} to download {out_fname} is unsuccessful. Checksums do NOT match")
                os.unlink(out_fname)
            retry_counter += 1
            time.sleep(args.sleep)
        else:
            log.info(f"Maximum number of retries reached for {out_fname}. Stopping any further attempts")




def main():
    """Do the downloads"""
    #<file label="0116_SJ02_MP02_10_MG"
    #filename="133140.assembled.fna"
    #size="2 GB"
    #sizeInBytes="2340006592"
    #timestamp="Tue Jun 06 19:34:49 PDT 2017"
    #url="/portal/ext-api/downloads/get_tape_file?blocking=true&amp;url=/0116_SJ02_MP02_1_3/download/_JAMO/5939a4d97ded5e4e5bbc0796/133140.assembled.fna"
    #project="1141571"
    #library=""
    #md5="fb4dd64d0ebbf11e0405a731fe03583f"
    #fileType="Assembly" />
    global DEBUG
    global VERBOSE
    args = parse_args()
    if args.debug:
        DEBUG = True
        VERBOSE = True
    if args.verbose:
        VERBOSE = True 
    log = setup_logger(debug=args.debug)
    log.info("Starting up")
    if DEBUG:
        log.debug("Debugging output is on")
    for infile in args.infiles:
        args.in_filename = infile
        records = {}
        if VERBOSE:
            log.info(f"Parsing: {infile} file")
        with open(infile, 'r') as fh:
            html_doc = fh.read()
            soup = bs(html_doc, features="lxml")
            for i in soup.find_all('file'):
                if i['filename'].endswith('tar.gz'):
                    rec = i.attrs
                    records[rec['label']] = rec
        if args.parseonly:
            for rec in records:
                rec_url = records[rec]['url']
                noblock_url = rec_url.replace("blocking=true", "blocking=false")
                wget_url = f"{base_url}{noblock_url}"
                log.info(f"URL: {wget_url}")
            sys.exit(0)
        if VERBOSE:
            log.info(f"Records from {infile}:")
            for i in records:
                if DEBUG:
                    log.debug(records[i])
                else:
                    log.info(f"URL for {i}: {records[i]['url']}")
        cj = get_cookies() 
        download_records(args, records, cj)
    

if __name__ == '__main__':
    main()
