import argparse
import sys
import os
import shipyard_utils as shipyard
try:
    import helpers
except BaseException:
    from . import helpers


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', dest='base_url', required=True)
    parser.add_argument('--client-id', dest='client_id', required=True)
    parser.add_argument('--client-secret', dest='client_secret', required=True)
    parser.add_argument('--filters', dest='filters', required=False)
    args = parser.parse_args()
    return args


def create_query(look_sdk, body={}):
    try:
        # Options are csv, json, json_detail, txt, html, md, xlsx, sql (raw query), png, jpg
        new_query = look_sdk.create_query(
            body=body
        )
        print("query {new_query.id} created successfully")
    except Exception as e:
        print(f'Error running create query: {e}')
    return new_query.id


def main():
    args = get_args()
    base_url = args.base_url
    client_id = args.client_id
    client_secret = args.client_secret
    if args.filters:
        filters = args.filters
    else:
        filters = {}

    # generate SDK
    look_sdk = helpers.get_sdk(base_url, client_id, client_secret)
    
    # download look and write to file
    new_query_id = create_query(look_sdk, body=filters)
    
    artifact_subfolder_paths = helpers.artifact_subfolder_paths
    shipyard.logs.create_pickle_file(artifact_subfolder_paths, 
                                                   'query_id', new_query_id)


if __name__ == "__main__":
    main()
    