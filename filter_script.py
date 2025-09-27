import os
import sys
from git_filter_repo import RepoFilter, cli

def filter_callback(blob, metadata):
    old_path = b"c:/users/ddr/onedrive/documents/local_freelancer_final/local_free_lancer_new"
    new_path = b"Local_Free_Lancer_New"
    
    if old_path in blob.data:
        blob.data = blob.data.replace(old_path, new_path)

if __name__ == '__main__':
    # Pass the arguments to the command-line interface via a list
    sys.argv = [
        'git-filter-repo',
        '--force',
        '--blob-callback', 'filter_callback',
    ]

    # Run the main entry point
    cli.main()