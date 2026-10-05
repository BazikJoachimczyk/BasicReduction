"""
Upload calibrated FITS frames to BHTOM2 (https://bh-tom2.astrouw.edu.pl), skipping
frames that are already there.

For every .fits/.fit file in the folder the script:
  1. checks the local ledger (bhtom_uploads.json in the folder) for a previous upload,
  2. asks BHTOM (POST /common/api/data/) whether a fits_file data product with this
     file name already exists for this observatory and user,
  3. uploads the file (POST https://uploadsvc2.bh-tom2.astrouw.edu.pl/upload/) if neither found it.

Example:
    python bhtom_upload.py --token <API_TOKEN> --folder D:/obs/2026-10-04/reduced \
        --observatory ROAD_QHY600M --observers jdoe asmith --target Gaia22bpl

If --target is omitted, the target name is read from the OBJECT keyword of each FITS header.
API docs: https://github.com/BHTOM-Team/bhtom2/blob/master/Documentation/DocumentationAPI.md
"""
import argparse
import json
import sys
import time
from datetime import datetime, timezone
from os import listdir
from os.path import basename, isfile, join, splitext

import requests
from astropy.io import fits

BHTOM_URL = 'https://bh-tom2.astrouw.edu.pl'
UPLOAD_URL = 'https://uploadsvc2.bh-tom2.astrouw.edu.pl/upload/'
LEDGER_NAME = 'bhtom_uploads.json'
FITS_EXTENSIONS = ('.fits', '.fit', '.fts')
TIMEOUT = 120


class BhtomClient:
    def __init__(self, token: str):
        self.session = requests.Session()
        self.session.headers['Authorization'] = f'Token {token}'

    def current_user(self) -> dict:
        response = self.session.get(f'{BHTOM_URL}/common/api/users/me/', timeout=TIMEOUT)
        if response.status_code == 401:
            raise SystemExit('BHTOM rejected the API token (401 Unauthorized).')
        response.raise_for_status()
        return response.json()

    def find_data_products(self, file_name: str, oname: str) -> list:
        """
        Returns fits_file data products whose fits_data URL contains file_name.
        The endpoint lists data products of all users, 500 per page.
        """
        found = []
        page = 1
        while True:
            body = {
                'data_product_type': 'fits_file',
                'fits_data': file_name,
                'oname': oname,
                'page': page,
            }
            response = self.session.post(f'{BHTOM_URL}/common/api/data/', json=body, timeout=TIMEOUT)
            response.raise_for_status()
            result = response.json()
            found.extend(result.get('data', []))
            # An out-of-range page returns the last page again, so stop on num_pages.
            if page >= result.get('num_pages', 1):
                return found
            page += 1

    def upload_fits(self, path: str, target: str, oname: str, observers: list, filter_name: str,
                    comment: str = None, match_dist: str = None, dry_run: bool = False) -> requests.Response:
        data = {
            'target': target,
            'filter': filter_name,
            'data_product_type': 'fits_file',
            'dry_run': str(dry_run),
            'observatory': oname,
            'observers': observers,
        }
        if comment:
            data['comment'] = comment
        if match_dist:
            data['match_dist'] = match_dist
        with open(path, 'rb') as f:
            return self.session.post(UPLOAD_URL, data=data, files={'files': (basename(path), f)},
                                     timeout=TIMEOUT)


def load_ledger(folder: str) -> dict:
    path = join(folder, LEDGER_NAME)
    if not isfile(path):
        return {}
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_ledger(folder: str, ledger: dict) -> None:
    with open(join(folder, LEDGER_NAME), 'w', encoding='utf-8') as f:
        json.dump(ledger, f, indent=2)


def list_fits_files(folder: str) -> list:
    return sorted(join(folder, name) for name in listdir(folder)
                  if isfile(join(folder, name)) and name.lower().endswith(FITS_EXTENSIONS))


def target_from_header(path: str) -> str:
    with fits.open(path) as hdul:
        target = hdul[0].header.get('OBJECT')
    return str(target).strip() if target else None


def matches_file(product: dict, file_name: str, username: str, include_all_users: bool) -> bool:
    """Server filter is a substring match - confirm the file name and owner on our side."""
    if product.get('dryRun'):
        return False
    if not include_all_users and product.get('user') != username:
        return False
    url = (product.get('fits_data') or '').rstrip('/')
    stored_name = url.rsplit('/', 1)[-1]
    # Upload service may add a prefix to the stored name or change .fit -> .fits.
    return file_name in stored_name or f'{splitext(file_name)[0]}.' in stored_name


def describe(product: dict) -> str:
    return (f"id={product.get('id')} status={product.get('status')} "
            f"target={product.get('target_name')} created={product.get('created')}")


def parse_args():
    parser = argparse.ArgumentParser(description='Upload calibrated FITS frames to BHTOM2, skipping ones already uploaded.')
    parser.add_argument('--token', required=True, help='BHTOM API token')
    parser.add_argument('--folder', required=True, help='Folder with calibrated FITS frames')
    parser.add_argument('--observatory', required=True, help='Observatory ONAME (camera prefix) as registered in BHTOM')
    parser.add_argument('--observers', nargs='+', required=True,
                        help='BHTOM usernames of observers (case sensitive), space separated')
    parser.add_argument('--target', default=None,
                        help='BHTOM target name; if omitted, taken from the OBJECT keyword of each FITS header')
    parser.add_argument('--filter', default='GaiaSP/any', help="Calibration filter (default: 'GaiaSP/any')")
    parser.add_argument('--comment', default=None, help='Comment attached to the upload')
    parser.add_argument('--match-dist', default=None, help='Matching radius in arcsec (default: auto)')
    parser.add_argument('--dry-run', action='store_true',
                        help='BHTOM processes the files but does not store results in the database')
    parser.add_argument('--check-only', action='store_true', help='Only report which files are already uploaded')
    parser.add_argument('--retry-errors', action='store_true',
                        help='Re-upload files whose existing BHTOM data product has status E (error)')
    parser.add_argument('--any-user', action='store_true',
                        help='Treat a file as uploaded even if another BHTOM user uploaded it')
    return parser.parse_args()


def main():
    args = parse_args()
    client = BhtomClient(args.token)
    username = client.current_user()['username']
    print(f'Authenticated as {username}')

    files = list_fits_files(args.folder)
    if not files:
        sys.exit(f'No FITS files found in {args.folder}')

    ledger = load_ledger(args.folder)
    counts = {'uploaded': 0, 'skipped': 0, 'failed': 0, 'to_upload': 0}

    for i, path in enumerate(files, 1):
        file_name = basename(path)
        prefix = f'[{i}/{len(files)}] {file_name}:'

        target = args.target or target_from_header(path)
        if not target:
            print(f'{prefix} no --target given and no OBJECT keyword in header - skipped')
            counts['failed'] += 1
            continue

        entry = ledger.get(file_name)
        if entry and not entry.get('dry_run') and not args.retry_errors:
            print(f"{prefix} already uploaded (local ledger, {entry.get('uploaded_at')})")
            counts['skipped'] += 1
            continue

        try:
            products = [p for p in client.find_data_products(file_name, args.observatory)
                        if matches_file(p, file_name, username, args.any_user)]
        except requests.RequestException as e:
            print(f'{prefix} could not check BHTOM ({e}) - skipped')
            counts['failed'] += 1
            continue

        ok_products = [p for p in products if p.get('status') != 'E']
        if ok_products or (products and not args.retry_errors):
            print(f'{prefix} already in BHTOM ({describe((ok_products or products)[0])})')
            counts['skipped'] += 1
            continue

        if args.check_only:
            print(f'{prefix} NOT uploaded (target {target})')
            counts['to_upload'] += 1
            continue

        print(f'{prefix} uploading (target {target})...')
        try:
            response = client.upload_fits(path, target, args.observatory, args.observers, args.filter,
                                          args.comment, args.match_dist, args.dry_run)
        except requests.RequestException as e:
            print(f'{prefix} upload failed: {e}')
            counts['failed'] += 1
            continue

        try:
            body = response.json()
        except ValueError:
            body = response.text

        if response.status_code in (200, 201):
            print(f'{prefix} OK {body}')
            counts['uploaded'] += 1
            ledger[file_name] = {
                'target': target,
                'observatory': args.observatory,
                'observers': args.observers,
                'dry_run': args.dry_run,
                'uploaded_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                'response': body,
            }
            save_ledger(args.folder, ledger)
        else:
            print(f'{prefix} upload rejected (HTTP {response.status_code}): {body}')
            counts['failed'] += 1
        time.sleep(0.2)

    print(json.dumps(counts))
    sys.exit(1 if counts['failed'] else 0)


if __name__ == '__main__':
    main()
